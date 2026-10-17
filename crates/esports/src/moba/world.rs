// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! A MOBA world: the template a package defines, and the world the
//! generator builds from it (world generation spec).

use domain::date::GameDate;
use domain::id::ContentId;
use domain::rating::Rating;
use domain::world::{Competition, NamePool, Nationality, Region, Team, WorldSettings};

use super::attributes::MobaAttributes;
use super::content::{GenerationParams, PinnedPlayer, RosterRules};
use super::roles::RoleSet;

/// Everything a package defines, already validated.
#[derive(Debug, Clone)]
pub struct WorldTemplate {
    pub settings: WorldSettings,
    pub regions: Vec<Region>,
    pub nationalities: Vec<Nationality>,
    pub name_pools: Vec<NamePool>,
    /// Without case-insensitive repeats.
    pub nicknames: Vec<String>,
    pub competitions: Vec<Competition>,
    pub teams: Vec<Team>,
    pub players: Vec<PinnedPlayer>,
    pub roles: RoleSet,
    pub roster: RosterRules,
    pub generation: GenerationParams,
}

/// A player on a roster.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Player {
    pub id: ContentId,
    pub team: ContentId,
    /// The main role.
    pub role: ContentId,
    pub starter: bool,
    pub nickname: String,
    pub given_name: String,
    pub family_name: String,
    pub nationality: ContentId,
    pub birth_date: GameDate,
    pub attributes: MobaAttributes,
}

/// A generated world, ready to be saved.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct World {
    pub settings: WorldSettings,
    pub regions: Vec<Region>,
    pub nationalities: Vec<Nationality>,
    pub competitions: Vec<Competition>,
    /// In id order.
    pub teams: Vec<Team>,
    pub roles: RoleSet,
    /// Team by team in id order; on each team, pinned players in id order,
    /// then generated players in the order they were created.
    pub players: Vec<Player>,
}

impl World {
    /// A player's overall, with the weights of their main role.
    #[must_use]
    pub fn overall(&self, player: &Player) -> Option<Rating> {
        self.roles
            .get(&player.role)
            .map(|role| role.overall(&player.attributes))
    }
}
