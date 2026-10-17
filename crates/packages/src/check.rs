// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Checks across entities: unique ids, references that resolve, text that
//! exists, and content the generator can always use (packages and world
//! generation specs). A package that passes never makes New Game fail.

use std::collections::{BTreeMap, BTreeSet};

use app::content::ContentText;
use app::content::{NameKind, PackageError, Problem};
use domain::date::GameDate;
use domain::id::ContentId;
use domain::world::{Competition, NamePool, Nationality, Region, Team};
use esports::moba::content::{GenerationParams, PinnedPlayer, RosterRules};
use esports::moba::roles::{Role, RoleSet};
use fluent_syntax::ast;

use crate::convert::Located;
use crate::parse::{Entry, Parsed};

/// Everything that converted cleanly, by kind.
pub struct Content<'a> {
    pub regions: &'a [Located<Region>],
    pub nationalities: &'a [Located<Nationality>],
    pub name_pools: &'a [Located<NamePool>],
    pub nicknames: &'a [Located<Vec<String>>],
    pub competitions: &'a [Located<Competition>],
    pub teams: &'a [Located<Team>],
    pub players: &'a [Located<PinnedPlayer>],
    pub roles: Option<&'a Located<(RoleSet, RosterRules)>>,
    pub generation: Option<&'a Located<GenerationParams>>,
    pub start_date: Option<GameDate>,
}

/// What the definitions declare, as written. It is read before conversion
/// takes the definitions apart, and an entity that failed to convert for an
/// unrelated reason still counts: references to it don't cascade into a
/// second, misleading error, and a manifest with an unrelated mistake
/// doesn't hide every text problem.
pub struct Declared {
    regions: BTreeSet<ContentId>,
    nationalities: BTreeSet<ContentId>,
    teams: BTreeSet<ContentId>,
    /// `None` when the package has no role set.
    roles: Option<BTreeSet<ContentId>>,
    /// `None` when the package has no manifest.
    locales: Option<Vec<String>>,
}

/// Checks that ids are unique, and reads what the definitions declare.
pub fn declared(parsed: &Parsed, errors: &mut Vec<PackageError>) -> Declared {
    duplicates(parsed, errors);
    let roles = (!parsed.role_sets.is_empty()).then(|| {
        parsed
            .role_sets
            .iter()
            .flat_map(|set| &set.def.roles)
            .filter_map(|role| ContentId::parse(&role.id).ok())
            .collect()
    });
    Declared {
        regions: defined(&parsed.regions, |d| &d.id),
        nationalities: defined(&parsed.nationalities, |d| &d.id),
        teams: defined(&parsed.teams, |d| &d.id),
        roles,
        locales: parsed
            .manifest
            .as_ref()
            .map(|manifest| manifest.def.locales.clone()),
    }
}

pub fn check(
    declared: &Declared,
    texts: &[ContentText],
    content: &Content<'_>,
    errors: &mut Vec<PackageError>,
) {
    references(declared, content, errors);
    if let Some(locales) = &declared.locales {
        text(texts, content, locales, errors);
    }
    mixes_and_pools(content, errors);
    duplicate_nicknames(content, errors);
    birth_dates(content, errors);
    if let Some(roles) = content.roles
        && rosters(content, roles, errors)
        && let Some(generation) = content.generation
    {
        nickname_pool(
            content,
            roles.value.1,
            &roles.value.0,
            &generation.value,
            errors,
        );
    }
}

fn duplicates(parsed: &Parsed, errors: &mut Vec<PackageError>) {
    fn ids<T>(
        entries: &[Entry<T>],
        id: impl Fn(&T) -> &str,
    ) -> impl Iterator<Item = (&str, &str, String)> {
        entries
            .iter()
            .map(move |entry| (id(&entry.def), entry.file.as_str(), entry.at("id")))
    }
    let all = ids(&parsed.competitions, |d| &d.id)
        .chain(ids(&parsed.generations, |d| &d.id))
        .chain(ids(&parsed.name_pools, |d| &d.id))
        .chain(ids(&parsed.nationalities, |d| &d.id))
        .chain(ids(&parsed.nicknames, |d| &d.id))
        .chain(ids(&parsed.players, |d| &d.id))
        .chain(ids(&parsed.regions, |d| &d.id))
        .chain(ids(&parsed.role_sets, |d| &d.id))
        .chain(ids(&parsed.teams, |d| &d.id));
    let mut seen: BTreeMap<&str, &str> = BTreeMap::new();
    for (text, file, path) in all {
        let Ok(id) = ContentId::parse(text) else {
            continue;
        };
        match seen.get(text) {
            Some(first) => errors.push(PackageError::new(
                file,
                path,
                Problem::DuplicateId {
                    id,
                    other_file: (*first).to_owned(),
                },
            )),
            None => {
                seen.insert(text, file);
            }
        }
    }
}

/// The ids a package defines, as written.
fn defined<T>(entries: &[Entry<T>], id: impl Fn(&T) -> &str) -> BTreeSet<ContentId> {
    entries
        .iter()
        .filter_map(|entry| ContentId::parse(id(&entry.def)).ok())
        .collect()
}

fn references(declared: &Declared, content: &Content<'_>, errors: &mut Vec<PackageError>) {
    let Declared {
        regions,
        nationalities,
        teams,
        roles,
        locales: _,
    } = declared;

    let mut require = |set: &BTreeSet<ContentId>,
                       at: &dyn Fn(Problem) -> PackageError,
                       field: &str,
                       id: &ContentId| {
        if !set.contains(id) {
            errors.push(at(Problem::UnresolvedReference {
                field: field.to_owned(),
                id: id.to_string(),
            }));
        }
    };

    for region in content.regions {
        for (nationality, _) in &region.value.nationalities {
            let field = format!("nationalities.{nationality}");
            require(
                nationalities,
                &|p| region.error(&field, p),
                &field,
                nationality,
            );
        }
    }
    for pool in content.name_pools {
        require(
            nationalities,
            &|p| pool.error("nationality", p),
            "nationality",
            &pool.value.nationality,
        );
    }
    for competition in content.competitions {
        let value = &competition.value;
        require(
            regions,
            &|p| competition.error("region", p),
            "region",
            &value.region,
        );
        for (index, team) in value.teams.iter().enumerate() {
            let field = format!("teams[{index}]");
            require(teams, &|p| competition.error(&field, p), &field, team);
        }
    }
    for team in content.teams {
        require(
            regions,
            &|p| team.error("region", p),
            "region",
            &team.value.region,
        );
    }
    for player in content.players {
        let value = &player.value;
        require(teams, &|p| player.error("team", p), "team", &value.team);
        if let Some(roles) = roles {
            require(roles, &|p| player.error("role", p), "role", &value.role);
        }
        if let Some(nationality) = &value.nationality {
            require(
                nationalities,
                &|p| player.error("nationality", p),
                "nationality",
                nationality,
            );
        }
    }
}

fn text(
    texts: &[ContentText],
    content: &Content<'_>,
    locales: &[String],
    errors: &mut Vec<PackageError>,
) {
    let mut messages: BTreeMap<&str, BTreeSet<String>> = BTreeMap::new();
    for file in texts {
        if !locales.contains(&file.locale) {
            errors.push(PackageError::new(
                &file.file,
                "",
                Problem::UnknownLocale {
                    locale: file.locale.clone(),
                },
            ));
            continue;
        }
        let Some(resource) = parse_text(&file.source, |line| {
            errors.push(PackageError::new(
                &file.file,
                "",
                Problem::TextSyntax { line },
            ));
        }) else {
            continue;
        };
        let ids = messages.entry(file.locale.as_str()).or_default();
        for entry in resource.body {
            if let ast::Entry::Message(message) = entry {
                ids.insert(message.id.name.to_owned());
            }
        }
    }

    let Some(first) = locales.first() else {
        return;
    };
    let empty = BTreeSet::new();
    let defined = messages.get(first.as_str()).unwrap_or(&empty);
    let mut require = |id: &ContentId, at: &dyn Fn(Problem) -> PackageError| {
        let message = id.message_id();
        if !defined.contains(&message) {
            errors.push(at(Problem::MissingText {
                message,
                locale: first.clone(),
            }));
        }
    };
    for region in content.regions {
        require(&region.value.id, &|p| region.error("id", p));
    }
    for nationality in content.nationalities {
        require(&nationality.value.id, &|p| nationality.error("id", p));
    }
    for competition in content.competitions {
        require(&competition.value.id, &|p| competition.error("id", p));
    }
    for team in content.teams {
        require(&team.value.id, &|p| team.error("id", p));
    }
    if let Some(roles) = content.roles {
        for (index, role) in roles.value.0.roles().iter().enumerate() {
            require(role.id(), &|p| {
                roles.error(&format!("roles[{index}].id"), p)
            });
        }
    }
}

/// The line `offset` falls on, counting from 1.
fn line_of(source: &str, offset: usize) -> usize {
    source.get(..offset).unwrap_or(source).matches('\n').count() + 1
}

/// A unicode escape (`\u` with four hex digits, `\U` with six) that is cut
/// short by a non-ASCII character: fluent-syntax 0.12 panics on it instead of
/// reporting it, so it is caught here first.
fn broken_escape(source: &str) -> Option<usize> {
    for (offset, _) in source.match_indices('\\') {
        let rest = &source[offset + 1..];
        let digits = match rest.chars().next() {
            Some('u') => 4,
            Some('U') => 6,
            _ => continue,
        };
        let window: Vec<char> = rest.chars().skip(1).take(digits).collect();
        let cut_short = window
            .iter()
            .position(|c| !c.is_ascii_hexdigit())
            .is_some_and(|position| !window[position].is_ascii());
        if cut_short {
            return Some(line_of(source, offset));
        }
    }
    None
}

/// Parses a package's `.ftl` text, reporting each syntax error's line. The
/// parser must never take the game down, so a panic in it is reported as a
/// syntax error too.
fn parse_text(source: &str, mut report: impl FnMut(usize)) -> Option<ast::Resource<&str>> {
    if let Some(line) = broken_escape(source) {
        report(line);
        return None;
    }
    match std::panic::catch_unwind(|| fluent_syntax::parser::parse(source)) {
        Ok(Ok(resource)) => Some(resource),
        Ok(Err((resource, problems))) => {
            for problem in problems {
                report(line_of(source, problem.pos.start));
            }
            Some(resource)
        }
        Err(_) => {
            report(1);
            None
        }
    }
}

fn mixes_and_pools(content: &Content<'_>, errors: &mut Vec<PackageError>) {
    let mut drawable = BTreeSet::new();
    for region in content.regions {
        let mix = &region.value.nationalities;
        let total: u64 = mix.iter().map(|&(_, weight)| u64::from(weight)).sum();
        if total == 0 {
            errors.push(region.error(
                "nationalities",
                Problem::InvalidMix {
                    region: region.value.id.clone(),
                },
            ));
        }
        drawable.extend(
            mix.iter()
                .filter(|(_, weight)| *weight > 0)
                .map(|(id, _)| id),
        );
    }
    // A pinned nationality draws names too, even when both are pinned: every
    // draw happens, so pinning one field never shifts another.
    drawable.extend(
        content
            .players
            .iter()
            .filter_map(|p| p.value.nationality.as_ref()),
    );
    for nationality in content.nationalities {
        let id = &nationality.value.id;
        if !drawable.contains(id) {
            continue;
        }
        let pools = content
            .name_pools
            .iter()
            .filter(|pool| &pool.value.nationality == id);
        let (mut given, mut family) = (false, false);
        for pool in pools {
            given |= !pool.value.given.is_empty();
            family |= !pool.value.family.is_empty();
        }
        for (has, names) in [(given, NameKind::Given), (family, NameKind::Family)] {
            if !has {
                errors.push(nationality.error(
                    "id",
                    Problem::EmptyNamePool {
                        nationality: id.clone(),
                        names,
                    },
                ));
            }
        }
    }
}

/// Pinned nicknames are unique, ignoring case.
fn duplicate_nicknames(content: &Content<'_>, errors: &mut Vec<PackageError>) {
    let mut nicknames: BTreeMap<String, &ContentId> = BTreeMap::new();
    for player in content.players {
        let Some(nickname) = &player.value.nickname else {
            continue;
        };
        match nicknames.get(&nickname.to_lowercase()) {
            Some(&other) => errors.push(player.error(
                "nickname",
                Problem::DuplicateNickname {
                    nickname: nickname.clone(),
                    player: player.value.id.clone(),
                    other: other.clone(),
                },
            )),
            None => {
                nicknames.insert(nickname.to_lowercase(), &player.value.id);
            }
        }
    }
}

/// A pinned birth date can't be after the world's start: the player would
/// have no age.
fn birth_dates(content: &Content<'_>, errors: &mut Vec<PackageError>) {
    let Some(start) = content.start_date else {
        return;
    };
    for player in content.players {
        if player.value.birth_date.is_some_and(|born| born > start) {
            errors.push(player.error("birth_date", Problem::OutOfRange));
        }
    }
}

/// Checks the roster shape and pinned rosters. Returns whether the roster
/// shape itself is usable.
fn rosters(
    content: &Content<'_>,
    located: &Located<(RoleSet, RosterRules)>,
    errors: &mut Vec<PackageError>,
) -> bool {
    let (role_set, rules) = &located.value;
    let role_count = role_set.roles().len();
    if usize::from(rules.subs) > role_count {
        errors.push(located.error(
            "subs",
            Problem::TooManySubs {
                subs: rules.subs,
                roles: role_count,
            },
        ));
        return false;
    }

    for team in content.teams {
        let mut counts: BTreeMap<&ContentId, usize> = BTreeMap::new();
        for player in content
            .players
            .iter()
            .filter(|p| p.value.team == team.value.id)
        {
            *counts.entry(&player.value.role).or_default() += 1;
        }
        let doubled = counts.values().filter(|&&count| count >= 2).count();
        let crowded = counts.values().any(|&count| count > 2);
        if crowded || doubled > usize::from(rules.subs) {
            let missing_roles = role_set
                .roles()
                .iter()
                .map(Role::id)
                .filter(|id| !counts.contains_key(id))
                .cloned()
                .collect();
            errors.push(team.error(
                "id",
                Problem::IncompletableRoster {
                    team: team.value.id.clone(),
                    missing_roles,
                },
            ));
        }
    }
    true
}

fn nickname_pool(
    content: &Content<'_>,
    rules: RosterRules,
    role_set: &RoleSet,
    generation: &GenerationParams,
    errors: &mut Vec<PackageError>,
) {
    let pinned: BTreeSet<String> = content
        .players
        .iter()
        .filter_map(|player| player.value.nickname.as_ref())
        .map(|nickname| nickname.to_lowercase())
        .collect();
    let distinct = content
        .nicknames
        .iter()
        .flat_map(|pool| &pool.value)
        .map(|nickname| nickname.to_lowercase())
        .filter(|nickname| !pinned.contains(nickname))
        .collect::<BTreeSet<_>>()
        .len();
    // Every roster place draws a nickname unless its player pins one,
    // including pinned players who leave their nickname out.
    let roster_size = role_set.roles().len() + usize::from(rules.subs);
    let places = content.teams.len().saturating_mul(roster_size);
    let pinned_nicknames = content
        .players
        .iter()
        // A pinned player on an unknown team is reported on its own.
        .filter(|p| p.value.nickname.is_some())
        .count();
    let generated = places.saturating_sub(pinned_nicknames);
    let factor = usize::try_from(generation.common.nickname_pool_factor).unwrap_or(usize::MAX);
    let needed = generated.saturating_mul(factor);
    if distinct < needed {
        let file = content
            .nicknames
            .first()
            .map_or_else(|| "nicknames/".to_owned(), |pool| pool.file.clone());
        errors.push(PackageError::new(
            file,
            "",
            Problem::NicknamePoolTooSmall { distinct, needed },
        ));
    }
}

#[cfg(test)]
mod tests {
    /// Caught before parsing, so fluent-syntax never panics: the loader's
    /// `catch_unwind` is only a backstop.
    #[test]
    fn cut_short_escapes_are_found_before_parsing() {
        assert!(super::broken_escape("a = { \"\\u00é\" }").is_some());
        assert!(super::broken_escape("a = { \"\\U0001é\" }").is_some());
        assert_eq!(
            super::broken_escape("a = { \"\\u00e9 \\U01F600\" } é"),
            None
        );
    }
}
