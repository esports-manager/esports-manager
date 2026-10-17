// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! MOBA content a package defines beyond the shared world structure: pinned
//! players, the roster shape and the generator's constants.

use domain::date::GameDate;
use domain::generation::Constants;
use domain::id::ContentId;
use domain::rating::Rating;

/// Attributes a package pins on a player. Every `None` is generated.
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq)]
pub struct PinnedAttributes {
    pub mechanics: Option<Rating>,
    pub laning: Option<Rating>,
    pub game_sense: Option<Rating>,
    pub awareness: Option<Rating>,
    pub positioning: Option<Rating>,
    pub champion_pool_breadth: Option<Rating>,
    pub shotcalling: Option<Rating>,
    pub teamwork: Option<Rating>,
    pub aggression: Option<Rating>,
    pub composure: Option<Rating>,
    pub work_ethic: Option<Rating>,
    pub consistency: Option<Rating>,
    pub potential: Option<Rating>,
}

/// A player a package defines by hand. Every field left out is generated as
/// if the player were generated for their team.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PinnedPlayer {
    pub id: ContentId,
    pub team: ContentId,
    pub role: ContentId,
    pub nickname: Option<String>,
    pub given_name: Option<String>,
    pub family_name: Option<String>,
    pub nationality: Option<ContentId>,
    pub birth_date: Option<GameDate>,
    pub attributes: PinnedAttributes,
}

/// How many players a roster has beyond one per role.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct RosterRules {
    pub subs: u8,
}

/// The generator's constants (world generation spec): the genre-agnostic
/// ones, and how MOBA skills spread around a player's base.
#[derive(Debug, Clone, PartialEq)]
pub struct GenerationParams {
    pub common: Constants,
    /// Spread of each attribute that counts toward overall around the
    /// player's base.
    pub attribute_spread: f64,
    /// Scale of the role bias.
    pub bias_scale: f64,
}
