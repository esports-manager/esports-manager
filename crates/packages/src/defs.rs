// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! The package file format: one Rust type per content type, from which the
//! loader deserializes and the JSON Schemas are generated (ADR 0005). These
//! types are the single definition of the format.
//!
//! Every type rejects unknown fields. Each accepts an optional `$schema`
//! field, which editors use to find the schema and the loader skips.

use std::collections::BTreeMap;

use schemars::JsonSchema;
use serde::Deserialize;

/// `manifest.json`.
#[derive(Debug, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct ManifestDef {
    #[serde(rename = "$schema", default)]
    pub schema: Option<String>,
    /// The package id: `a-z`, `0-9` and `_`.
    pub id: String,
    /// `major.minor.patch`.
    #[schemars(regex(pattern = r"^\d+\.\d+\.\d+$"))]
    pub version: String,
    pub title: String,
    /// An SPDX licence expression.
    pub license: String,
    pub authors: Vec<String>,
    /// The genre, such as `moba`.
    pub genre: String,
    /// The locales the package's text covers. The first one is the fallback.
    pub locales: Vec<String>,
}

/// `world.json`.
#[derive(Debug, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct WorldDef {
    #[serde(rename = "$schema", default)]
    pub schema: Option<String>,
    /// The first day of the game, as `YYYY-MM-DD`.
    #[schemars(regex(pattern = r"^\d{4}-\d{2}-\d{2}$"))]
    pub start_date: String,
}

/// A region, in `regions/`.
#[derive(Debug, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct RegionDef {
    #[serde(rename = "$schema", default)]
    pub schema: Option<String>,
    pub id: String,
    /// Added to every team's mean strength in this region.
    pub level: i32,
    /// Nationality ids and their weights. The total must be positive.
    #[serde(deserialize_with = "unique_keys")]
    pub nationalities: BTreeMap<String, u32>,
}

#[derive(Debug, Clone, Copy, Deserialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum NameOrderDef {
    GivenFirst,
    FamilyFirst,
}

/// A nationality, in `nationalities/`.
#[derive(Debug, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct NationalityDef {
    #[serde(rename = "$schema", default)]
    pub schema: Option<String>,
    pub id: String,
    /// ISO 3166-1 alpha-2, such as `KR`.
    #[schemars(regex(pattern = r"^[A-Z]{2}$"))]
    pub code: String,
    pub name_order: NameOrderDef,
}

/// Given and family names of one nationality, in `name-pools/`.
#[derive(Debug, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct NamePoolDef {
    #[serde(rename = "$schema", default)]
    pub schema: Option<String>,
    pub id: String,
    pub nationality: String,
    pub given: Vec<String>,
    pub family: Vec<String>,
}

/// Nicknames, in `nicknames/`. All pools are merged into one.
#[derive(Debug, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct NicknamePoolDef {
    #[serde(rename = "$schema", default)]
    pub schema: Option<String>,
    pub id: String,
    pub nicknames: Vec<String>,
}

/// A league, in `competitions/`.
#[derive(Debug, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct CompetitionDef {
    #[serde(rename = "$schema", default)]
    pub schema: Option<String>,
    pub id: String,
    pub region: String,
    pub teams: Vec<String>,
}

/// A team, in `teams/`.
#[derive(Debug, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct TeamDef {
    #[serde(rename = "$schema", default)]
    pub schema: Option<String>,
    pub id: String,
    pub region: String,
    /// Three uppercase letters or digits.
    #[schemars(regex(pattern = r"^[A-Z0-9]{3}$"))]
    pub tag: String,
    /// Two `#RRGGBB` colours: the crest's fill and its border.
    pub colours: [String; 2],
    /// 1 to 100.
    #[schemars(range(min = 1, max = 100))]
    pub reputation: u32,
}

/// Attributes pinned on a player, in whole points from 1 to 99.
#[derive(Debug, Clone, Default, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct PinnedAttributesDef {
    #[schemars(range(min = 1, max = 99))]
    pub mechanics: Option<u32>,
    #[schemars(range(min = 1, max = 99))]
    pub laning: Option<u32>,
    #[schemars(range(min = 1, max = 99))]
    pub game_sense: Option<u32>,
    #[schemars(range(min = 1, max = 99))]
    pub awareness: Option<u32>,
    #[schemars(range(min = 1, max = 99))]
    pub positioning: Option<u32>,
    #[schemars(range(min = 1, max = 99))]
    pub champion_pool_breadth: Option<u32>,
    #[schemars(range(min = 1, max = 99))]
    pub shotcalling: Option<u32>,
    #[schemars(range(min = 1, max = 99))]
    pub teamwork: Option<u32>,
    #[schemars(range(min = 1, max = 99))]
    pub aggression: Option<u32>,
    #[schemars(range(min = 1, max = 99))]
    pub composure: Option<u32>,
    #[schemars(range(min = 1, max = 99))]
    pub work_ethic: Option<u32>,
    #[schemars(range(min = 1, max = 99))]
    pub consistency: Option<u32>,
    #[schemars(range(min = 1, max = 99))]
    pub potential: Option<u32>,
}

/// A player pinned by hand, in `players/`. Every field left out is
/// generated.
#[derive(Debug, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct PlayerDef {
    #[serde(rename = "$schema", default)]
    pub schema: Option<String>,
    pub id: String,
    pub team: String,
    pub role: String,
    pub nickname: Option<String>,
    pub given_name: Option<String>,
    pub family_name: Option<String>,
    pub nationality: Option<String>,
    /// `YYYY-MM-DD`.
    #[schemars(regex(pattern = r"^\d{4}-\d{2}-\d{2}$"))]
    pub birth_date: Option<String>,
    #[serde(default)]
    pub attributes: PinnedAttributesDef,
}

/// The attributes that count toward overall, as weight keys.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Deserialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum WeightKey {
    Mechanics,
    Laning,
    GameSense,
    Awareness,
    Positioning,
    ChampionPoolBreadth,
    Shotcalling,
    Teamwork,
    Composure,
}

#[derive(Debug, Clone, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct RoleDef {
    pub id: String,
    /// The weight of every attribute that counts toward overall.
    #[serde(deserialize_with = "unique_keys")]
    pub weights: BTreeMap<WeightKey, u32>,
}

/// The role set and roster shape, in `roles/`. A package defines exactly one.
#[derive(Debug, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct RoleSetDef {
    #[serde(rename = "$schema", default)]
    pub schema: Option<String>,
    pub id: String,
    /// The roles, in display order.
    pub roles: Vec<RoleDef>,
    /// Players on a roster beyond one per role.
    pub subs: u8,
}

/// The generator's constants, in `generation/`. A package defines exactly
/// one. See the world generation spec for what each one does.
#[derive(Debug, Deserialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct GenerationDef {
    #[serde(rename = "$schema", default)]
    pub schema: Option<String>,
    pub id: String,
    pub mu_base: f64,
    pub mu_per_reputation: f64,
    pub sigma_base: f64,
    pub sigma_per_reputation: f64,
    #[schemars(range(min = 0.0))]
    pub sigma_min: f64,
    #[schemars(range(min = 0.0))]
    pub attribute_spread: f64,
    pub bias_scale: f64,
    pub style_mean: f64,
    #[schemars(range(min = 0.0))]
    pub style_spread: f64,
    pub consistency_mean: f64,
    #[schemars(range(min = 0.0))]
    pub consistency_spread: f64,
    pub potential_peak_age: f64,
    pub potential_per_year: f64,
    #[schemars(range(min = 0.0))]
    pub potential_spread: f64,
    pub age_mean: f64,
    #[schemars(range(min = 0.0))]
    pub age_spread: f64,
    pub age_min: u8,
    pub age_max: u8,
    #[schemars(range(min = 1))]
    pub nickname_pool_factor: u32,
}

/// What a content file holds: one entity, or a list of them. Only its
/// schema is used; the loader reads the two shapes itself.
#[derive(JsonSchema)]
#[serde(untagged)]
pub enum OneOrMany<T> {
    One(T),
    Many(Vec<T>),
}

/// A JSON object as a map that refuses a key given twice. Serde's own maps
/// keep the last value silently; the loader never silently falls back.
fn unique_keys<'de, D, K, V>(deserializer: D) -> Result<BTreeMap<K, V>, D::Error>
where
    D: serde::Deserializer<'de>,
    K: Deserialize<'de> + Ord,
    V: Deserialize<'de>,
{
    struct UniqueKeys<K, V>(std::marker::PhantomData<(K, V)>);

    impl<'de, K, V> serde::de::Visitor<'de> for UniqueKeys<K, V>
    where
        K: Deserialize<'de> + Ord,
        V: Deserialize<'de>,
    {
        type Value = BTreeMap<K, V>;

        fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
            formatter.write_str("an object")
        }

        fn visit_map<A: serde::de::MapAccess<'de>>(
            self,
            mut map: A,
        ) -> Result<Self::Value, A::Error> {
            use serde::de::{Error, IntoDeserializer};
            let mut values = BTreeMap::new();
            while let Some(text) = map.next_key::<String>()? {
                let key = K::deserialize(text.clone().into_deserializer())?;
                let value = map.next_value()?;
                if values.insert(key, value).is_some() {
                    // The loader reads this wording as `DuplicateField`.
                    return Err(A::Error::custom(format!("duplicate field `{text}`")));
                }
            }
            Ok(values)
        }
    }

    deserializer.deserialize_map(UniqueKeys(std::marker::PhantomData))
}
