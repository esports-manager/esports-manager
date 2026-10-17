// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! The world generator (world generation spec).
//!
//! Each team draws from its own stream (`generator:team:<team id>`), each
//! pinned player from theirs (`generator:player:<id>`), and each nickname
//! from `generator:nickname:<player id>`. Every player consumes the same
//! number of draws whatever is pinned, so pinning a field never shifts
//! another draw.
//!
//! The genre-agnostic draws (strength, birth date, nationality and names,
//! traits, potential, nicknames) are `domain::generation`'s; this module adds
//! roles, the MOBA skills and the roster shape.

use std::collections::{BTreeMap, BTreeSet};

use domain::generation::{self, DrawError, NamePools, Nicknames, Strength, Traits};
use domain::id::ContentId;
use domain::random::{index_excluding, normal};
use domain::rating::Rating;
use domain::rng::{StreamLabel, StreamSource};
use domain::world::{Region, Team};
use rand_core::Rng;

use super::attributes::{MobaAttributes, OverallAttribute};
use super::content::{GenerationParams, PinnedAttributes, PinnedPlayer};
use super::world::{Player, World, WorldTemplate};

/// Why a template can't be generated. The package loader rules all of
/// these out, so they only happen with a template built by hand.
#[derive(Debug, Clone, PartialEq, Eq, thiserror::Error)]
pub enum GenerationError {
    #[error("`{0}` refers to a region, role or nationality that doesn't exist")]
    Unknown(ContentId),
    #[error("region `{0}` has no nationality to draw")]
    EmptyMix(ContentId),
    #[error("nationality `{0}` has no given or family names")]
    EmptyNames(ContentId),
    #[error("team `{0}` can't complete its roster around its pinned players")]
    IncompletableRoster(ContentId),
    #[error("the nickname pool ran out")]
    NicknamesExhausted,
    #[error("player `{0}` is born after the world starts")]
    BornAfterStart(ContentId),
    #[error("the generator built an invalid id for team `{0}`")]
    InvalidId(ContentId),
}

/// Builds the world: every team's roster, around its pinned players.
///
/// # Errors
///
/// When the template refers to something it doesn't define, or can't
/// supply a draw. A template from a package that loaded never fails.
pub fn generate(
    mut template: WorldTemplate,
    streams: &impl StreamSource,
) -> Result<World, GenerationError> {
    template.teams.sort_by(|a, b| a.id.cmp(&b.id));
    if let Some(stray) = template
        .players
        .iter()
        .find(|p| !template.teams.iter().any(|t| t.id == p.team))
    {
        return Err(GenerationError::Unknown(stray.team.clone()));
    }
    let generator = Generator::new(&template);

    let mut players = Vec::new();
    for team in &template.teams {
        players.extend(generator.team(team, streams)?);
    }
    assign_nicknames(&template, &mut players, streams)?;
    pick_starters(&template, &mut players);

    // What only generation needs stays behind.
    let WorldTemplate {
        settings,
        regions,
        nationalities,
        name_pools: _,
        nicknames: _,
        competitions,
        teams,
        players: _,
        roles,
        roster: _,
        generation: _,
    } = template;
    Ok(World {
        settings,
        regions,
        nationalities,
        competitions,
        teams,
        roles,
        players,
    })
}

/// Generates players from one template.
struct Generator<'a> {
    template: &'a WorldTemplate,
    params: &'a GenerationParams,
    names: NamePools<'a>,
}

impl<'a> Generator<'a> {
    fn new(template: &'a WorldTemplate) -> Self {
        Self {
            template,
            params: &template.generation,
            names: NamePools::new(&template.name_pools),
        }
    }

    fn team(
        &self,
        team: &Team,
        streams: &impl StreamSource,
    ) -> Result<Vec<Player>, GenerationError> {
        let region = self
            .template
            .regions
            .iter()
            .find(|region| region.id == team.region)
            .ok_or_else(|| GenerationError::Unknown(team.region.clone()))?;
        let strength = Strength::of(&self.params.common, team.reputation, region.level);

        let mut pinned: Vec<&PinnedPlayer> = self
            .template
            .players
            .iter()
            .filter(|p| p.team == team.id)
            .collect();
        pinned.sort_by(|a, b| a.id.cmp(&b.id));

        let mut rng = streams.stream(&StreamLabel::new(format!("generator:team:{}", team.id)));
        let slots = self.slots(team, &pinned, &mut rng)?;

        let mut players = Vec::new();
        for player in pinned {
            let mut own =
                streams.stream(&StreamLabel::new(format!("generator:player:{}", player.id)));
            players.push(self.player(
                &mut own,
                player.id.clone(),
                team,
                region,
                strength,
                &player.role,
                Some(player),
            )?);
        }
        for (number, role) in (1..).zip(slots) {
            let id = ContentId::generated("player", &team.id, number)
                .map_err(|_| GenerationError::InvalidId(team.id.clone()))?;
            players.push(self.player(&mut rng, id, team, region, strength, &role, None)?);
        }
        Ok(players)
    }

    /// The roles of the players the generator adds to `team`: every role no
    /// pinned player covers, in role-set order, then subs in different roles
    /// drawn from the team's stream.
    fn slots(
        &self,
        team: &Team,
        pinned: &[&PinnedPlayer],
        rng: &mut impl Rng,
    ) -> Result<Vec<ContentId>, GenerationError> {
        let roles = self.template.roles.roles();
        let mut counts = vec![0_usize; roles.len()];
        for player in pinned {
            let position = roles
                .iter()
                .position(|role| role.id() == &player.role)
                .ok_or_else(|| GenerationError::Unknown(player.role.clone()))?;
            counts[position] += 1;
        }
        let missing: Vec<usize> = (0..roles.len()).filter(|&i| counts[i] == 0).collect();
        for &position in &missing {
            counts[position] = 1;
        }
        let size = roles.len() + usize::from(self.template.roster.subs);
        let remaining = size
            .checked_sub(pinned.len() + missing.len())
            .ok_or_else(|| GenerationError::IncompletableRoster(team.id.clone()))?;
        if counts.iter().any(|&count| count > 2) {
            return Err(GenerationError::IncompletableRoster(team.id.clone()));
        }

        // Subs go to roles that have exactly one player so far.
        let mut taken: BTreeSet<usize> = (0..roles.len()).filter(|&i| counts[i] != 1).collect();
        let mut subs = Vec::new();
        for _ in 0..remaining {
            let position = index_excluding(rng, roles.len(), &taken)
                .ok_or_else(|| GenerationError::IncompletableRoster(team.id.clone()))?;
            taken.insert(position);
            subs.push(position);
        }
        Ok(missing
            .into_iter()
            .chain(subs)
            .map(|position| roles[position].id().clone())
            .collect())
    }

    #[expect(
        clippy::too_many_arguments,
        reason = "each argument is distinct; a parameter struct would only rename them"
    )]
    fn player(
        &self,
        rng: &mut impl Rng,
        id: ContentId,
        team: &Team,
        region: &Region,
        strength: Strength,
        role_id: &ContentId,
        pinned: Option<&PinnedPlayer>,
    ) -> Result<Player, GenerationError> {
        let p = self.params;
        let role = self
            .template
            .roles
            .get(role_id)
            .ok_or_else(|| GenerationError::Unknown(role_id.clone()))?;

        // Every draw happens in this fixed order, pinned or not.
        let identity = self
            .names
            .draw(rng, region, pinned.and_then(|p| p.nationality.as_ref()))
            .map_err(|error| match error {
                DrawError::EmptyMix(region) => GenerationError::EmptyMix(region),
                DrawError::EmptyNames(nationality) => GenerationError::EmptyNames(nationality),
            })?;
        let birth_date = generation::birth_date(rng, &p.common, self.template.settings.start_date);
        let base = normal(rng, strength.mu, strength.sigma);
        let mut attributes = MobaAttributes::uniform(Rating::MIN);
        for attribute in OverallAttribute::ALL {
            let value = normal(
                rng,
                base + role.bias(attribute, p.bias_scale),
                p.attribute_spread,
            );
            *attributes.get_mut(attribute) = Rating::clamped(value);
        }
        let traits = Traits::draw(rng, &p.common);
        attributes.core.aggression = traits.aggression;
        attributes.core.work_ethic = traits.work_ethic;
        attributes.core.consistency = traits.consistency;

        let mut player = Player {
            id,
            team: team.id.clone(),
            role: role_id.clone(),
            starter: false,
            nickname: String::new(),
            given_name: identity.given_name,
            family_name: identity.family_name,
            nationality: identity.nationality,
            birth_date,
            attributes,
        };
        if let Some(pinned) = pinned {
            apply_pins(&mut player, pinned);
        }
        if pinned.and_then(|p| p.attributes.potential).is_none() {
            let overall = role.overall(&player.attributes).points();
            let age = player
                .birth_date
                .age_on(self.template.settings.start_date)
                .ok_or_else(|| GenerationError::BornAfterStart(player.id.clone()))?;
            player.attributes.core.potential =
                generation::potential(&p.common, overall, age, traits.potential_noise);
        }
        Ok(player)
    }
}

fn apply_pins(player: &mut Player, pinned: &PinnedPlayer) {
    if let Some(name) = &pinned.given_name {
        player.given_name.clone_from(name);
    }
    if let Some(name) = &pinned.family_name {
        player.family_name.clone_from(name);
    }
    if let Some(date) = pinned.birth_date {
        player.birth_date = date;
    }
    let PinnedAttributes {
        mechanics,
        laning,
        game_sense,
        awareness,
        positioning,
        champion_pool_breadth,
        shotcalling,
        teamwork,
        aggression,
        composure,
        work_ethic,
        consistency,
        potential,
    } = pinned.attributes;
    let skills = &mut player.attributes.skills;
    let core = &mut player.attributes.core;
    let pins = [
        (mechanics, &mut skills.mechanics),
        (laning, &mut skills.laning),
        (game_sense, &mut skills.game_sense),
        (awareness, &mut skills.awareness),
        (positioning, &mut skills.positioning),
        (champion_pool_breadth, &mut skills.champion_pool_breadth),
        (shotcalling, &mut skills.shotcalling),
        (teamwork, &mut core.teamwork),
        (aggression, &mut core.aggression),
        (composure, &mut core.composure),
        (work_ethic, &mut core.work_ethic),
        (consistency, &mut core.consistency),
        (potential, &mut core.potential),
    ];
    for (pin, field) in pins {
        if let Some(rating) = pin {
            *field = rating;
        }
    }
}

/// Gives every player without a pinned nickname one from the pool, each
/// drawn from the player's own stream.
fn assign_nicknames(
    template: &WorldTemplate,
    players: &mut [Player],
    streams: &impl StreamSource,
) -> Result<(), GenerationError> {
    let pinned: BTreeMap<&ContentId, &str> = template
        .players
        .iter()
        .filter_map(|p| p.nickname.as_deref().map(|nickname| (&p.id, nickname)))
        .collect();
    let mut pool = Nicknames::new(&template.nicknames, pinned.values().copied());
    for player in players {
        if let Some(nickname) = pinned.get(&player.id) {
            player.nickname = (*nickname).to_owned();
            continue;
        }
        let mut rng = streams.stream(&StreamLabel::new(format!(
            "generator:nickname:{}",
            player.id
        )));
        pool.draw(&mut rng)
            .ok_or(GenerationError::NicknamesExhausted)?
            .clone_into(&mut player.nickname);
    }
    Ok(())
}

/// For each team and role, the player with the highest overall starts; ties
/// go to the lower id.
fn pick_starters(template: &WorldTemplate, players: &mut [Player]) {
    let mut candidates: BTreeMap<(&ContentId, &ContentId), Vec<(Rating, &ContentId)>> =
        BTreeMap::new();
    for player in players.iter() {
        if let Some(role) = template.roles.get(&player.role) {
            candidates
                .entry((&player.team, &player.role))
                .or_default()
                .push((role.overall(&player.attributes), &player.id));
        }
    }
    let starters: BTreeSet<ContentId> = candidates
        .values()
        .filter_map(|group| {
            group
                .iter()
                .max_by(|a, b| a.0.cmp(&b.0).then_with(|| b.1.cmp(a.1)))
                .map(|&(_, id)| id.clone())
        })
        .collect();
    for player in players {
        player.starter = starters.contains(&player.id);
    }
}

#[cfg(test)]
#[path = "generation_tests.rs"]
mod tests;
