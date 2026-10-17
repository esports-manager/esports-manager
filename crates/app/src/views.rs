// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! View DTOs: exactly what each screen shows, already derived (ADR 0006).
//! The CLI's `--json` prints them as they are, so the CLI and the UI see the
//! same view. Fields holding a Fluent message id end in `message`.

use domain::attributes::{CoreTrait, HiddenAttribute};
use domain::id::ContentId;
use domain::world::{NameOrder, Team};
use esports::moba::attributes::{MobaSkill, OverallAttribute};
use serde::Serialize;

use crate::messages::Message;

/// A team's procedural crest: its tag on its first colour, bordered in its
/// second, with text Rust picked to stay readable (ADR 0010).
#[derive(Debug, Clone, PartialEq, Eq, Serialize, specta::Type)]
#[serde(rename_all = "camelCase")]
pub struct Crest {
    pub tag: String,
    pub fill: String,
    pub border: String,
    pub text: String,
}

impl Crest {
    #[must_use]
    pub fn of(team: &Team) -> Self {
        let [fill, border] = team.colours;
        Self {
            tag: team.tag.as_str().to_owned(),
            fill: fill.to_string(),
            border: border.to_string(),
            text: fill.readable_text().to_string(),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, specta::Type)]
#[serde(rename_all = "camelCase")]
pub struct TeamOption {
    pub id: String,
    pub name_message: String,
    pub crest: Crest,
    /// 1 to 5 stars: the ceiling of reputation / 20.
    pub strength: u8,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, specta::Type)]
#[serde(rename_all = "camelCase")]
pub struct RegionOption {
    pub id: String,
    pub name_message: String,
    pub league_id: Option<String>,
    pub league_message: Option<String>,
    pub teams: Vec<TeamOption>,
}

/// What New Game offers.
#[derive(Debug, PartialEq, Eq, Serialize, specta::Type)]
#[serde(rename_all = "camelCase")]
pub struct NewGameOptions {
    pub regions: Vec<RegionOption>,
}

/// Serialized as the selector key `person-full-name` expects, so the UI and
/// the CLI pass it to Fluent as it is.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, specta::Type)]
#[serde(rename_all = "kebab-case")]
pub enum NameOrderView {
    GivenFirst,
    FamilyFirst,
}

impl NameOrderView {
    /// The `$order` value of the `person-full-name` message.
    #[must_use]
    pub const fn as_str(self) -> &'static str {
        match self {
            Self::GivenFirst => "given-first",
            Self::FamilyFirst => "family-first",
        }
    }
}

impl From<NameOrder> for NameOrderView {
    fn from(order: NameOrder) -> Self {
        match order {
            NameOrder::GivenFirst => Self::GivenFirst,
            NameOrder::FamilyFirst => Self::FamilyFirst,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, specta::Type)]
#[serde(rename_all = "camelCase")]
pub struct NationalityView {
    pub id: String,
    /// ISO 3166-1 alpha-2, for the badge.
    pub code: String,
    pub name_message: String,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, specta::Type)]
#[serde(rename_all = "camelCase")]
pub struct TeamHeader {
    pub id: String,
    pub name_message: String,
    pub crest: Crest,
    pub region_message: String,
    pub league_message: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, specta::Type)]
#[serde(rename_all = "camelCase")]
pub struct RosterPlayer {
    pub id: String,
    pub nickname: String,
    pub given_name: String,
    pub family_name: String,
    pub name_order: NameOrderView,
    pub role_id: String,
    pub role_message: String,
    pub nationality: NationalityView,
    pub age: u16,
    pub overall: u8,
}

/// The roster screen: starters, then subs, each in role-set order.
#[derive(Debug, PartialEq, Eq, Serialize, specta::Type)]
#[serde(rename_all = "camelCase")]
pub struct RosterView {
    pub team: TeamHeader,
    pub starters: Vec<RosterPlayer>,
    pub subs: Vec<RosterPlayer>,
}

/// One attribute on the profile. Hidden attributes have no value.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, specta::Type)]
#[serde(rename_all = "camelCase")]
pub struct AttributeView {
    pub name_message: String,
    pub value: Option<u8>,
}

#[derive(Debug, PartialEq, Eq, Serialize, specta::Type)]
#[serde(rename_all = "camelCase")]
pub struct PlayerProfile {
    pub player: RosterPlayer,
    pub starter: bool,
    pub team: TeamHeader,
    /// `YYYY-MM-DD`.
    pub birth_date: String,
    pub skills: Vec<AttributeView>,
    pub traits: Vec<AttributeView>,
    pub hidden: Vec<AttributeView>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, specta::Type)]
#[serde(rename_all = "camelCase")]
pub enum DamageView {
    NotASave,
    NewerVersion,
}

/// One entry of Load Game.
#[derive(Debug, PartialEq, Eq, Serialize, specta::Type)]
#[serde(rename_all = "camelCase", tag = "status")]
pub enum SaveSummary {
    #[serde(rename_all = "camelCase")]
    Ready {
        file: String,
        /// Another process (or window) has it open, so it can't be opened.
        in_use: bool,
        name: String,
        manager_name: String,
        team_message: String,
        game_date: String,
        /// Seconds since the Unix epoch; the UI formats it. A JavaScript
        /// number holds it exactly.
        #[specta(type = u32)]
        last_played_at: i64,
    },
    #[serde(rename_all = "camelCase")]
    Damaged { file: String, damage: DamageView },
}

/// The save that is now open: the result of New Game and Load Game.
#[derive(Debug, PartialEq, Eq, Serialize, specta::Type)]
#[serde(rename_all = "camelCase")]
pub struct GameOpened {
    pub file: String,
    pub team: String,
    /// The team's name message.
    pub team_message: String,
}

impl GameOpened {
    #[must_use]
    pub fn new(file: String, team: &ContentId) -> Self {
        Self {
            file,
            team: team.to_string(),
            team_message: team.message_id(),
        }
    }
}

/// A use case's failure, as messages an adapter can show.
#[derive(Debug, PartialEq, Eq, Serialize, specta::Type)]
#[serde(rename_all = "camelCase")]
pub struct Failure {
    pub messages: Vec<Message>,
}

/// The message holding a content entity's name (packages spec).
#[must_use]
pub fn name_message(id: &ContentId) -> String {
    id.message_id()
}

/// The UI message naming an attribute.
#[must_use]
pub const fn attribute_message(attribute: OverallAttribute) -> &'static str {
    match attribute {
        OverallAttribute::Skill(skill) => skill_message(skill),
        OverallAttribute::Teamwork => trait_message(CoreTrait::Teamwork),
        OverallAttribute::Composure => trait_message(CoreTrait::Composure),
    }
}

#[must_use]
pub const fn skill_message(skill: MobaSkill) -> &'static str {
    match skill {
        MobaSkill::Mechanics => "attribute-mechanics",
        MobaSkill::Laning => "attribute-laning",
        MobaSkill::GameSense => "attribute-game-sense",
        MobaSkill::Awareness => "attribute-awareness",
        MobaSkill::Positioning => "attribute-positioning",
        MobaSkill::ChampionPoolBreadth => "attribute-champion-pool-breadth",
        MobaSkill::Shotcalling => "attribute-shotcalling",
    }
}

#[must_use]
pub const fn trait_message(core: CoreTrait) -> &'static str {
    match core {
        CoreTrait::Teamwork => "attribute-teamwork",
        CoreTrait::Aggression => "attribute-aggression",
        CoreTrait::Composure => "attribute-composure",
        CoreTrait::WorkEthic => "attribute-work-ethic",
    }
}

#[must_use]
pub const fn hidden_message(hidden: HiddenAttribute) -> &'static str {
    match hidden {
        HiddenAttribute::Consistency => "attribute-consistency",
        HiddenAttribute::Potential => "attribute-potential",
    }
}

/// 1 to 5 stars from a 1–100 reputation.
#[must_use]
pub fn strength_stars(reputation: u8) -> u8 {
    reputation.div_ceil(20).clamp(1, 5)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_name_order_reads_as_its_message_selector_and_its_json() {
        for (order, text) in [
            (NameOrderView::GivenFirst, "given-first"),
            (NameOrderView::FamilyFirst, "family-first"),
        ] {
            assert_eq!(order.as_str(), text);
            assert_eq!(serde_json::to_value(order).unwrap(), text);
        }
    }

    #[test]
    fn strength_stars_come_from_reputation() {
        // spec: NEWG-002
        // Given
        let reputations = [95, 41, 1];
        // When
        let stars = reputations.map(strength_stars);
        // Then
        assert_eq!(stars, [5, 3, 1]);
        assert_eq!([20, 21, 80, 81, 100].map(strength_stars), [1, 2, 4, 5, 5]);
    }

    #[test]
    fn every_attribute_has_its_own_message() {
        let mut ids: Vec<&str> = MobaSkill::ALL.iter().map(|&s| skill_message(s)).collect();
        ids.extend(CoreTrait::ALL.iter().map(|&t| trait_message(t)));
        ids.extend(HiddenAttribute::ALL.iter().map(|&h| hidden_message(h)));
        let distinct: std::collections::BTreeSet<&str> = ids.iter().copied().collect();
        assert_eq!(distinct.len(), 13);
        assert_eq!(
            attribute_message(OverallAttribute::Teamwork),
            "attribute-teamwork"
        );
        assert_eq!(
            attribute_message(OverallAttribute::Composure),
            "attribute-composure"
        );
        assert_eq!(
            attribute_message(OverallAttribute::Skill(MobaSkill::Laning)),
            "attribute-laning"
        );
    }

    #[test]
    fn name_orders_map_to_their_view() {
        assert_eq!(
            NameOrderView::from(NameOrder::GivenFirst),
            NameOrderView::GivenFirst
        );
        assert_eq!(
            NameOrderView::from(NameOrder::FamilyFirst),
            NameOrderView::FamilyFirst
        );
    }
}
