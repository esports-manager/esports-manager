// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Row types: the only place Diesel types meet domain types (ADR 0001 rule
//! 3). Every conversion is written out field by field, and every enum maps
//! through one exhaustive function each way (ADR 0004).

use diesel::prelude::*;
use domain::date::GameDate;
use domain::id::ContentId;
use domain::rating::Rating;
use domain::world::{Colour, CountryCode, NameOrder, Nationality, Reputation, Tag, Team};
use esports::Genre;
use esports::moba::attributes::{MobaAttributes, MobaSkills, OverallAttribute};
use esports::moba::world::Player;

use crate::schema::{
    competition_teams, competitions, content_texts, nationalities, packages, players,
    region_nationalities, regions, roles, save_meta, teams,
};
use app::saves::SaveError;

/// A value read back from a save that doesn't fit its domain type.
pub fn corrupt(what: &str, value: &str) -> SaveError {
    SaveError::Storage(format!("the save holds an invalid {what}: `{value}`"))
}

pub fn id(text: &str) -> Result<ContentId, SaveError> {
    ContentId::parse_stored(text).map_err(|_| corrupt("id", text))
}

pub fn date(text: &str) -> Result<GameDate, SaveError> {
    text.parse().map_err(|_| corrupt("date", text))
}

pub fn rating(hundredths: i32) -> Result<Rating, SaveError> {
    u32::try_from(hundredths)
        .ok()
        .and_then(|value| Rating::from_hundredths(value).ok())
        .ok_or_else(|| corrupt("rating", &hundredths.to_string()))
}

pub fn hundredths(rating: Rating) -> i32 {
    i32::from(rating.hundredths())
}

pub const fn name_order_to_db(order: NameOrder) -> &'static str {
    match order {
        NameOrder::GivenFirst => "given_first",
        NameOrder::FamilyFirst => "family_first",
    }
}

pub fn name_order_from_db(text: &str) -> Result<NameOrder, SaveError> {
    match text {
        "given_first" => Ok(NameOrder::GivenFirst),
        "family_first" => Ok(NameOrder::FamilyFirst),
        other => Err(corrupt("name order", other)),
    }
}

pub const fn genre_to_db(genre: Genre) -> &'static str {
    genre.id()
}

pub fn genre_from_db(text: &str) -> Result<Genre, SaveError> {
    text.parse().map_err(|_| corrupt("genre", text))
}

/// A seed is a `u64`; SQLite integers are `i64`. The bits are kept as they
/// are.
pub const fn seed_to_db(seed: u64) -> i64 {
    i64::from_ne_bytes(seed.to_ne_bytes())
}

pub const fn seed_from_db(value: i64) -> u64 {
    u64::from_ne_bytes(value.to_ne_bytes())
}

/// Positions are small; a world with more than `i32::MAX` rows of a kind
/// can't be saved.
pub fn position(index: usize) -> Result<i32, SaveError> {
    i32::try_from(index).map_err(|_| SaveError::Storage("too many rows to save".to_owned()))
}

#[derive(Debug, Insertable, Queryable, Selectable, AsChangeset)]
#[diesel(table_name = save_meta)]
pub struct SaveMetaRow {
    pub id: i32,
    pub name: String,
    pub manager_name: String,
    pub team_id: String,
    pub genre: String,
    pub seed: i64,
    pub game_version: String,
    pub game_date: String,
    pub created_at: i64,
    pub last_played_at: i64,
}

#[derive(Debug, Insertable, Queryable, Selectable)]
#[diesel(table_name = packages)]
pub struct PackageRow {
    pub id: String,
    pub position: i32,
    pub version: String,
    pub content_hash: Vec<u8>,
}

#[derive(Debug, Insertable, Queryable, Selectable)]
#[diesel(table_name = content_texts)]
pub struct TextRow {
    pub locale: String,
    pub file: String,
    pub source: String,
}

#[derive(Debug, Insertable, Queryable, Selectable)]
#[diesel(table_name = nationalities)]
pub struct NationalityRow {
    pub id: String,
    pub position: i32,
    pub code: String,
    pub name_order: String,
}

impl NationalityRow {
    pub fn into_domain(self) -> Result<Nationality, SaveError> {
        let Self {
            id: text,
            position: _,
            code,
            name_order,
        } = self;
        Ok(Nationality {
            id: id(&text)?,
            code: CountryCode::parse(&code).ok_or_else(|| corrupt("country code", &code))?,
            name_order: name_order_from_db(&name_order)?,
        })
    }
}

#[derive(Debug, Insertable, Queryable, Selectable)]
#[diesel(table_name = regions)]
pub struct RegionRow {
    pub id: String,
    pub position: i32,
    pub level: i32,
}

#[derive(Debug, Insertable, Queryable, Selectable)]
#[diesel(table_name = region_nationalities)]
pub struct RegionNationalityRow {
    pub region_id: String,
    pub nationality_id: String,
    pub weight: i32,
}

#[derive(Debug, Insertable, Queryable, Selectable)]
#[diesel(table_name = teams)]
pub struct TeamRow {
    pub id: String,
    pub position: i32,
    pub region_id: String,
    pub tag: String,
    pub colour_fill: String,
    pub colour_border: String,
    pub reputation: i32,
}

impl TeamRow {
    pub fn from_domain(team: &Team, index: usize) -> Result<Self, SaveError> {
        let Team {
            id,
            region,
            tag,
            colours: [fill, border],
            reputation,
        } = team;
        Ok(Self {
            id: id.to_string(),
            position: position(index)?,
            region_id: region.to_string(),
            tag: tag.as_str().to_owned(),
            colour_fill: fill.to_string(),
            colour_border: border.to_string(),
            reputation: i32::from(reputation.value()),
        })
    }

    pub fn into_domain(self) -> Result<Team, SaveError> {
        let Self {
            id: text,
            position: _,
            region_id,
            tag,
            colour_fill,
            colour_border,
            reputation,
        } = self;
        let colour = |text: &str| Colour::parse(text).ok_or_else(|| corrupt("colour", text));
        Ok(Team {
            id: id(&text)?,
            region: id(&region_id)?,
            tag: Tag::parse(&tag).ok_or_else(|| corrupt("tag", &tag))?,
            colours: [colour(&colour_fill)?, colour(&colour_border)?],
            reputation: u32::try_from(reputation)
                .ok()
                .and_then(Reputation::new)
                .ok_or_else(|| corrupt("reputation", &reputation.to_string()))?,
        })
    }
}

#[derive(Debug, Insertable, Queryable, Selectable)]
#[diesel(table_name = competitions)]
pub struct CompetitionRow {
    pub id: String,
    pub position: i32,
    pub region_id: String,
}

#[derive(Debug, Insertable, Queryable, Selectable)]
#[diesel(table_name = competition_teams)]
pub struct CompetitionTeamRow {
    pub competition_id: String,
    pub position: i32,
    pub team_id: String,
}

#[derive(Debug, Insertable, Queryable, Selectable)]
#[diesel(table_name = roles)]
pub struct RoleRow {
    pub id: String,
    pub position: i32,
    pub mechanics_weight: i32,
    pub laning_weight: i32,
    pub game_sense_weight: i32,
    pub awareness_weight: i32,
    pub positioning_weight: i32,
    pub champion_pool_breadth_weight: i32,
    pub shotcalling_weight: i32,
    pub teamwork_weight: i32,
    pub composure_weight: i32,
}

impl RoleRow {
    pub fn from_domain(role: &esports::moba::roles::Role, index: usize) -> Result<Self, SaveError> {
        let weight = |attribute: OverallAttribute| {
            i32::try_from(role.weight(attribute))
                .map_err(|_| SaveError::Storage("weight too large".to_owned()))
        };
        let [
            mechanics,
            laning,
            game_sense,
            awareness,
            positioning,
            breadth,
            shotcalling,
            teamwork,
            composure,
        ] = OverallAttribute::ALL;
        Ok(Self {
            id: role.id().to_string(),
            position: position(index)?,
            mechanics_weight: weight(mechanics)?,
            laning_weight: weight(laning)?,
            game_sense_weight: weight(game_sense)?,
            awareness_weight: weight(awareness)?,
            positioning_weight: weight(positioning)?,
            champion_pool_breadth_weight: weight(breadth)?,
            shotcalling_weight: weight(shotcalling)?,
            teamwork_weight: weight(teamwork)?,
            composure_weight: weight(composure)?,
        })
    }

    /// The role's id and its weights in [`OverallAttribute::ALL`] order.
    pub fn into_parts(self) -> Result<(ContentId, [u32; 9]), SaveError> {
        let Self {
            id: text,
            position: _,
            mechanics_weight,
            laning_weight,
            game_sense_weight,
            awareness_weight,
            positioning_weight,
            champion_pool_breadth_weight,
            shotcalling_weight,
            teamwork_weight,
            composure_weight,
        } = self;
        let row = [
            mechanics_weight,
            laning_weight,
            game_sense_weight,
            awareness_weight,
            positioning_weight,
            champion_pool_breadth_weight,
            shotcalling_weight,
            teamwork_weight,
            composure_weight,
        ];
        let mut weights = [0; 9];
        for (slot, value) in weights.iter_mut().zip(row) {
            *slot = u32::try_from(value).map_err(|_| corrupt("weight", &value.to_string()))?;
        }
        Ok((id(&text)?, weights))
    }
}

#[derive(Debug, Insertable, Queryable, Selectable)]
#[diesel(table_name = players)]
pub struct PlayerRow {
    pub id: String,
    pub position: i32,
    pub team_id: String,
    pub role_id: String,
    pub starter: bool,
    pub nickname: String,
    pub given_name: String,
    pub family_name: String,
    pub nationality_id: String,
    pub birth_date: String,
    pub mechanics: i32,
    pub laning: i32,
    pub game_sense: i32,
    pub awareness: i32,
    pub positioning: i32,
    pub champion_pool_breadth: i32,
    pub shotcalling: i32,
    pub teamwork: i32,
    pub aggression: i32,
    pub composure: i32,
    pub work_ethic: i32,
    pub consistency: i32,
    pub potential: i32,
}

impl PlayerRow {
    pub fn from_domain(player: Player, index: usize) -> Result<Self, SaveError> {
        let Player {
            id,
            team,
            role,
            starter,
            nickname,
            given_name,
            family_name,
            nationality,
            birth_date,
            attributes: MobaAttributes { core, skills },
        } = player;
        Ok(Self {
            id: id.to_string(),
            position: position(index)?,
            team_id: team.to_string(),
            role_id: role.to_string(),
            starter,
            nickname,
            given_name,
            family_name,
            nationality_id: nationality.to_string(),
            birth_date: birth_date.to_string(),
            mechanics: hundredths(skills.mechanics),
            laning: hundredths(skills.laning),
            game_sense: hundredths(skills.game_sense),
            awareness: hundredths(skills.awareness),
            positioning: hundredths(skills.positioning),
            champion_pool_breadth: hundredths(skills.champion_pool_breadth),
            shotcalling: hundredths(skills.shotcalling),
            teamwork: hundredths(core.teamwork),
            aggression: hundredths(core.aggression),
            composure: hundredths(core.composure),
            work_ethic: hundredths(core.work_ethic),
            consistency: hundredths(core.consistency),
            potential: hundredths(core.potential),
        })
    }

    pub fn into_domain(self) -> Result<Player, SaveError> {
        let Self {
            id: text,
            position: _,
            team_id,
            role_id,
            starter,
            nickname,
            given_name,
            family_name,
            nationality_id,
            birth_date,
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
        } = self;
        Ok(Player {
            id: id(&text)?,
            team: id(&team_id)?,
            role: id(&role_id)?,
            starter,
            nickname,
            given_name,
            family_name,
            nationality: id(&nationality_id)?,
            birth_date: date(&birth_date)?,
            attributes: MobaAttributes {
                core: domain::attributes::CoreAttributes {
                    teamwork: rating(teamwork)?,
                    aggression: rating(aggression)?,
                    composure: rating(composure)?,
                    work_ethic: rating(work_ethic)?,
                    consistency: rating(consistency)?,
                    potential: rating(potential)?,
                },
                skills: MobaSkills {
                    mechanics: rating(mechanics)?,
                    laning: rating(laning)?,
                    game_sense: rating(game_sense)?,
                    awareness: rating(awareness)?,
                    positioning: rating(positioning)?,
                    champion_pool_breadth: rating(champion_pool_breadth)?,
                    shotcalling: rating(shotcalling)?,
                },
            },
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn enums_round_trip_through_their_text() {
        for order in [NameOrder::GivenFirst, NameOrder::FamilyFirst] {
            assert_eq!(name_order_from_db(name_order_to_db(order)), Ok(order));
        }
        for genre in Genre::ALL {
            assert_eq!(genre_from_db(genre_to_db(genre)), Ok(genre));
        }
        assert!(name_order_from_db("sideways").is_err());
        assert!(genre_from_db("chess").is_err());
    }

    #[test]
    fn seeds_keep_every_bit() {
        for seed in [0, 1, 42, u64::MAX, 1 << 63] {
            assert_eq!(seed_from_db(seed_to_db(seed)), seed);
        }
        assert_eq!(seed_to_db(u64::MAX), -1);
    }

    #[test]
    fn invalid_values_read_back_are_storage_errors() {
        assert!(id("Team").is_err());
        assert!(date("yesterday").is_err());
        assert!(rating(99).is_err());
        assert!(rating(-1).is_err());
        assert_eq!(rating(9900).map(Rating::hundredths), Ok(9900));
        assert_eq!(hundredths(Rating::MAX), 9900);
        assert_eq!(position(3), Ok(3));
        assert!(position(usize::MAX).is_err());
    }
}
