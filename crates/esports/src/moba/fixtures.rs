// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! A small, valid world template for tests in other crates: one region,
//! two teams, one pinned player. Enabled by the `test-support` feature.
#![allow(
    clippy::unwrap_used,
    clippy::missing_panics_doc,
    reason = "test support, which panics on a broken fixture"
)]

use std::collections::BTreeMap;

use domain::id::ContentId;
use domain::rng::{StreamLabel, StreamSource, WorldSeed, derive_stream_seed};
use domain::world::{
    Colour, Competition, CountryCode, NameOrder, NamePool, Nationality, Region, Reputation, Tag,
    Team, WorldSettings,
};
use rand_chacha::ChaCha8Rng;
use rand_core::SeedableRng;

use super::attributes::OverallAttribute;
use super::content::{GenerationParams, PinnedAttributes, PinnedPlayer, RosterRules};
use super::generation::generate;
use super::roles::RoleSet;
use super::world::{World, WorldTemplate};
use domain::generation::Constants;

/// The same streams the application's RNG provider hands out.
pub struct Seeded(pub WorldSeed);

impl StreamSource for Seeded {
    type Stream = ChaCha8Rng;

    fn stream(&self, label: &StreamLabel) -> ChaCha8Rng {
        ChaCha8Rng::from_seed(derive_stream_seed(self.0, label))
    }
}

#[must_use]
pub fn id(text: &str) -> ContentId {
    ContentId::parse(text).unwrap()
}

fn team(slug: &str, reputation: u32) -> Team {
    Team {
        id: id(&format!("team:{slug}")),
        region: id("region:r"),
        tag: Tag::parse("AAA").unwrap(),
        colours: [
            Colour::parse("#1E5AA8").unwrap(),
            Colour::parse("#F2C14E").unwrap(),
        ],
        reputation: Reputation::new(reputation).unwrap(),
    }
}

#[must_use]
pub fn template() -> WorldTemplate {
    let rows = [
        ("top", [16, 18, 14, 10, 12, 6, 4, 10, 10]),
        ("jungle", [14, 6, 20, 14, 8, 6, 14, 10, 8]),
        ("mid", [20, 16, 14, 10, 12, 8, 6, 6, 8]),
        ("bot", [20, 18, 10, 10, 16, 6, 4, 8, 8]),
        ("support", [10, 12, 14, 16, 12, 6, 14, 10, 6]),
    ];
    let roles = RoleSet::new(
        rows.iter()
            .map(|(slug, row)| {
                (
                    id(&format!("role:{slug}")),
                    OverallAttribute::ALL
                        .into_iter()
                        .zip(*row)
                        .collect::<BTreeMap<_, _>>(),
                )
            })
            .collect(),
    )
    .unwrap();
    let teams = vec![team("a", 80), team("b", 40)];
    WorldTemplate {
        settings: WorldSettings {
            start_date: "2027-01-01".parse().unwrap(),
        },
        regions: vec![Region {
            id: id("region:r"),
            level: 4,
            nationalities: vec![(id("nationality:br"), 1), (id("nationality:kr"), 9)],
        }],
        nationalities: vec![
            Nationality {
                id: id("nationality:kr"),
                code: CountryCode::parse("KR").unwrap(),
                name_order: NameOrder::FamilyFirst,
            },
            Nationality {
                id: id("nationality:br"),
                code: CountryCode::parse("BR").unwrap(),
                name_order: NameOrder::GivenFirst,
            },
        ],
        name_pools: vec![
            NamePool {
                nationality: id("nationality:kr"),
                given: vec!["Do-yun".into(), "Seo-jun".into()],
                family: vec!["Han".into()],
            },
            NamePool {
                nationality: id("nationality:br"),
                given: vec!["Caio".into()],
                family: vec!["Ribeiro".into(), "Silva".into()],
            },
        ],
        nicknames: (0..60).map(|n| format!("Nick{n}")).collect(),
        competitions: vec![Competition {
            id: id("competition:league"),
            region: id("region:r"),
            teams: teams.iter().map(|t| t.id.clone()).collect(),
        }],
        teams,
        players: vec![PinnedPlayer {
            id: id("player:kairos"),
            team: id("team:a"),
            role: id("role:mid"),
            nickname: Some("Kairos".into()),
            given_name: Some("Do-yun".into()),
            family_name: Some("Han".into()),
            nationality: Some(id("nationality:kr")),
            birth_date: Some("1997-03-14".parse().unwrap()),
            attributes: PinnedAttributes::default(),
        }],
        roles,
        roster: RosterRules { subs: 2 },
        generation: GenerationParams {
            common: Constants {
                mu_base: 35.0,
                mu_per_reputation: 0.4,
                sigma_base: 12.0,
                sigma_per_reputation: 0.07,
                sigma_min: 2.0,
                style_mean: 50.0,
                style_spread: 15.0,
                consistency_mean: 55.0,
                consistency_spread: 15.0,
                potential_peak_age: 24.0,
                potential_per_year: 2.5,
                potential_spread: 6.0,
                age_mean: 22.0,
                age_spread: 2.5,
                age_min: 17,
                age_max: 28,
                nickname_pool_factor: 3,
            },
            attribute_spread: 6.0,
            bias_scale: 8.0,
        },
    }
}

/// The template's world for `seed`.
#[must_use]
pub fn world(seed: u64) -> World {
    generate(template(), &Seeded(WorldSeed::new(seed))).unwrap()
}
