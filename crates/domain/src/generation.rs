// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! The genre-agnostic half of world generation (world generation spec,
//! ADR 0002): team strength, ages and birth dates, nationality and names,
//! nicknames, and the core traits every genre's players have. A genre's
//! generator calls these in a fixed order and adds what only it knows, such
//! as skills and roles.
//!
//! Every function here draws a fixed number of values whatever the outcome,
//! so a genre that pins a field after drawing it never shifts a later draw.

use std::collections::{BTreeMap, BTreeSet};

use rand_core::Rng;

use crate::date::GameDate;
use crate::id::ContentId;
use crate::random::{below, index, index_excluding, normal, round_clamped, weighted_index};
use crate::rating::Rating;
use crate::world::{NamePool, Region, Reputation};

/// The generator's genre-agnostic constants (`generation/` in a package).
/// Starting values, to be tuned in sim-bench.
#[derive(Debug, Clone, PartialEq)]
pub struct Constants {
    /// The team mean is `mu_base` + `mu_per_reputation` × reputation + region level.
    pub mu_base: f64,
    pub mu_per_reputation: f64,
    /// The team spread is max(`sigma_min`, `sigma_base` − `sigma_per_reputation` × reputation).
    pub sigma_base: f64,
    pub sigma_per_reputation: f64,
    pub sigma_min: f64,
    /// Aggression and Work Ethic.
    pub style_mean: f64,
    pub style_spread: f64,
    pub consistency_mean: f64,
    pub consistency_spread: f64,
    /// Potential gains `potential_per_year` for each year under this age.
    pub potential_peak_age: f64,
    pub potential_per_year: f64,
    pub potential_spread: f64,
    pub age_mean: f64,
    pub age_spread: f64,
    pub age_min: u8,
    pub age_max: u8,
    /// The nickname pool needs this many distinct entries per generated player.
    pub nickname_pool_factor: u32,
}

/// A team's player-base distribution: N(`mu`, `sigma`).
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Strength {
    pub mu: f64,
    pub sigma: f64,
}

impl Strength {
    /// A higher reputation gives a higher mean and a lower spread; the
    /// region's level shifts the mean.
    #[must_use]
    pub fn of(constants: &Constants, reputation: Reputation, level: i32) -> Self {
        let reputation = f64::from(reputation.value());
        Self {
            mu: constants.mu_base + constants.mu_per_reputation * reputation + f64::from(level),
            sigma: (constants.sigma_base - constants.sigma_per_reputation * reputation)
                .max(constants.sigma_min),
        }
    }
}

/// A birth date that gives an age drawn from N(`age_mean`, `age_spread`),
/// clamped to the allowed ages, on `start`. Draws two values.
pub fn birth_date(rng: &mut impl Rng, constants: &Constants, start: GameDate) -> GameDate {
    let age = round_clamped(
        normal(rng, constants.age_mean, constants.age_spread),
        i32::from(constants.age_min),
        i32::from(constants.age_max),
    );
    let age = u16::try_from(age).unwrap_or(0);
    // Born on `latest` turns `age` on the start date; one day before
    // `earliest`, they would already be a year older.
    let latest = start.years_before(age).unwrap_or(GameDate::MIN);
    let earliest = start
        .years_before(age + 1)
        .and_then(|date| date.add_days(1))
        .unwrap_or(GameDate::MIN);
    let span = latest.day_number() - earliest.day_number() + 1;
    let offset = below(rng, u64::try_from(span).unwrap_or(1)).unwrap_or(0);
    earliest
        .add_days(i64::try_from(offset).unwrap_or(0))
        .unwrap_or(latest)
}

/// Why a nationality or name couldn't be drawn. A package that loaded rules
/// both out.
#[derive(Debug, PartialEq, Eq)]
pub enum DrawError {
    /// The region has no nationality to draw.
    EmptyMix(ContentId),
    /// The nationality has no given or family names.
    EmptyNames(ContentId),
}

/// Who a player is: nationality and names.
#[derive(Debug, PartialEq, Eq)]
pub struct Identity {
    pub nationality: ContentId,
    pub given_name: String,
    pub family_name: String,
}

/// Given and family names by nationality, every pool merged and sorted, so
/// how a package splits its files never changes the world.
#[derive(Debug)]
pub struct NamePools<'a> {
    names: BTreeMap<&'a ContentId, (Vec<&'a str>, Vec<&'a str>)>,
}

impl<'a> NamePools<'a> {
    #[must_use]
    pub fn new(pools: &'a [NamePool]) -> Self {
        let mut names: BTreeMap<&ContentId, (Vec<&str>, Vec<&str>)> = BTreeMap::new();
        for pool in pools {
            let entry = names.entry(&pool.nationality).or_default();
            entry.0.extend(pool.given.iter().map(String::as_str));
            entry.1.extend(pool.family.iter().map(String::as_str));
        }
        for (given, family) in names.values_mut() {
            for list in [given, family] {
                list.sort_unstable();
                list.dedup();
            }
        }
        Self { names }
    }

    /// Draws a nationality from `region`'s mix, then a given and a family
    /// name from that nationality's pools. A `pinned` nationality replaces
    /// the drawn one; the mix is drawn anyway. Draws three values.
    ///
    /// # Errors
    ///
    /// When the mix or the nationality's pools are empty.
    pub fn draw(
        &self,
        rng: &mut impl Rng,
        region: &Region,
        pinned: Option<&ContentId>,
    ) -> Result<Identity, DrawError> {
        let weights: Vec<u32> = region
            .nationalities
            .iter()
            .map(|&(_, weight)| weight)
            .collect();
        let drawn =
            weighted_index(rng, &weights).ok_or_else(|| DrawError::EmptyMix(region.id.clone()))?;
        let nationality = pinned
            .cloned()
            .unwrap_or_else(|| region.nationalities[drawn].0.clone());
        let empty = || DrawError::EmptyNames(nationality.clone());
        let (given_pool, family_pool) = self.names.get(&nationality).ok_or_else(empty)?;
        let given = index(rng, given_pool.len()).ok_or_else(empty)?;
        let family = index(rng, family_pool.len()).ok_or_else(empty)?;
        Ok(Identity {
            given_name: given_pool[given].to_owned(),
            family_name: family_pool[family].to_owned(),
            nationality,
        })
    }
}

/// The core traits drawn the same way in every genre, and the noise of the
/// player's potential.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Traits {
    pub aggression: Rating,
    pub work_ethic: Rating,
    pub consistency: Rating,
    /// Added to the potential formula; see [`potential`].
    pub potential_noise: f64,
}

impl Traits {
    /// Aggression and Work Ethic from N(`style_mean`, `style_spread`),
    /// Consistency from N(`consistency_mean`, `consistency_spread`), then the
    /// potential noise from N(0, `potential_spread`). Draws four values.
    pub fn draw(rng: &mut impl Rng, constants: &Constants) -> Self {
        let aggression = Rating::clamped(normal(rng, constants.style_mean, constants.style_spread));
        let work_ethic = Rating::clamped(normal(rng, constants.style_mean, constants.style_spread));
        let consistency = Rating::clamped(normal(
            rng,
            constants.consistency_mean,
            constants.consistency_spread,
        ));
        let potential_noise = normal(rng, 0.0, constants.potential_spread);
        Self {
            aggression,
            work_ethic,
            consistency,
            potential_noise,
        }
    }
}

/// Potential: max(overall, overall + `potential_per_year` × years under
/// `potential_peak_age` + noise), clamped to a rating. Young players have
/// more room to grow. `overall` is the genre's overall for the player.
#[must_use]
pub fn potential(constants: &Constants, overall: f64, age: u16, noise: f64) -> Rating {
    let youth = (constants.potential_peak_age - f64::from(age)).max(0.0);
    let potential = overall + constants.potential_per_year * youth + noise;
    Rating::clamped(potential.max(overall))
}

/// How many times a player redraws a taken nickname before falling back to
/// a draw among the free ones only.
const NICKNAME_TRIES: u32 = 32;

/// One nickname pool, unique in the world ignoring case.
///
/// The pool is sorted first, so how a package splits it across files never
/// matters. Each player draws from the whole pool and redraws only when the
/// nickname is taken, so another player changes it only by taking the very
/// one drawn (world generation spec).
#[derive(Debug)]
pub struct Nicknames<'a> {
    pool: Vec<&'a str>,
    taken: BTreeSet<usize>,
}

impl<'a> Nicknames<'a> {
    /// The pool without repeats (ignoring case), with `pinned` nicknames
    /// already taken.
    pub fn new<'p>(pool: &'a [String], pinned: impl IntoIterator<Item = &'p str>) -> Self {
        let mut pool: Vec<&str> = pool.iter().map(String::as_str).collect();
        pool.sort_by_cached_key(|nickname| (nickname.to_lowercase(), (*nickname).to_owned()));
        pool.dedup_by_key(|nickname| nickname.to_lowercase());
        let pinned: BTreeSet<String> = pinned.into_iter().map(str::to_lowercase).collect();
        let taken = pool
            .iter()
            .enumerate()
            .filter(|(_, nickname)| pinned.contains(&nickname.to_lowercase()))
            .map(|(position, _)| position)
            .collect();
        Self { pool, taken }
    }

    /// A free nickname, drawn from `rng`, now taken. `None` once the pool
    /// has run out.
    pub fn draw(&mut self, rng: &mut impl Rng) -> Option<&'a str> {
        let position = self.free(rng)?;
        self.taken.insert(position);
        Some(self.pool[position])
    }

    fn free(&self, rng: &mut impl Rng) -> Option<usize> {
        for _ in 0..NICKNAME_TRIES {
            let position = index(rng, self.pool.len())?;
            if !self.taken.contains(&position) {
                return Some(position);
            }
        }
        index_excluding(rng, self.pool.len(), &self.taken)
    }
}

#[cfg(test)]
#[path = "generation_tests.rs"]
mod tests;
