// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Generator tests against small templates built in code. Statistical
//! scenarios use fixed seeds, so they are deterministic.

use std::collections::BTreeMap;

use domain::id::ContentId;
use domain::rating::Rating;
use domain::rng::{StreamLabel, StreamSource, WorldSeed, derive_stream_seed};
use domain::world::{
    Colour, Competition, CountryCode, NameOrder, NamePool, Nationality, Region, Reputation, Tag,
    Team, WorldSettings,
};
use rand_chacha::ChaCha8Rng;
use rand_core::SeedableRng;

use super::*;
use crate::moba::attributes::{MobaSkill, OverallAttribute};
use crate::moba::content::{GenerationParams, PinnedAttributes, PinnedPlayer, RosterRules};
use crate::moba::roles::RoleSet;
use domain::generation::Constants;

/// The same streams the application's RNG provider hands out.
struct Seeded(WorldSeed);

impl StreamSource for Seeded {
    type Stream = ChaCha8Rng;

    fn stream(&self, label: &StreamLabel) -> ChaCha8Rng {
        ChaCha8Rng::from_seed(derive_stream_seed(self.0, label))
    }
}

fn seed(value: u64) -> Seeded {
    Seeded(WorldSeed::new(value))
}

fn id(text: &str) -> ContentId {
    ContentId::parse(text).unwrap()
}

fn rating(points: u32) -> Rating {
    Rating::from_points(points).unwrap()
}

const CORE_WEIGHTS: [(&str, [u32; 9]); 5] = [
    ("top", [16, 18, 14, 10, 12, 6, 4, 10, 10]),
    ("jungle", [14, 6, 20, 14, 8, 6, 14, 10, 8]),
    ("mid", [20, 16, 14, 10, 12, 8, 6, 6, 8]),
    ("bot", [20, 18, 10, 10, 16, 6, 4, 8, 8]),
    ("support", [10, 12, 14, 16, 12, 6, 14, 10, 6]),
];

fn roles(slugs: &[(&str, [u32; 9])]) -> RoleSet {
    RoleSet::new(
        slugs
            .iter()
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
    .unwrap()
}

fn team(slug: &str, region: &str, reputation: u32) -> Team {
    Team {
        id: id(&format!("team:{slug}")),
        region: id(&format!("region:{region}")),
        tag: Tag::parse("AAA").unwrap(),
        colours: [
            Colour::parse("#000000").unwrap(),
            Colour::parse("#FFFFFF").unwrap(),
        ],
        reputation: Reputation::new(reputation).unwrap(),
    }
}

fn params() -> GenerationParams {
    GenerationParams {
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
    }
}

/// Two regions: `up` (level +4, 94% Korean) and `down` (level −4, Brazilian).
fn template(teams: Vec<Team>) -> WorldTemplate {
    let nationality = |slug: &str, code: &str, order| Nationality {
        id: id(&format!("nationality:{slug}")),
        code: CountryCode::parse(code).unwrap(),
        name_order: order,
    };
    let pool = |slug: &str, given: &[&str], family: &[&str]| NamePool {
        nationality: id(&format!("nationality:{slug}")),
        given: given.iter().map(|&s| s.to_owned()).collect(),
        family: family.iter().map(|&s| s.to_owned()).collect(),
    };
    WorldTemplate {
        settings: WorldSettings {
            start_date: "2027-01-01".parse().unwrap(),
        },
        regions: vec![
            Region {
                id: id("region:up"),
                level: 4,
                nationalities: vec![(id("nationality:br"), 6), (id("nationality:kr"), 94)],
            },
            Region {
                id: id("region:down"),
                level: -4,
                nationalities: vec![(id("nationality:br"), 1)],
            },
        ],
        nationalities: vec![
            nationality("kr", "KR", NameOrder::FamilyFirst),
            nationality("br", "BR", NameOrder::GivenFirst),
        ],
        name_pools: vec![
            pool("kr", &["Do-yun", "Seo-jun", "Ha-eun"], &["Han", "Kim"]),
            pool("br", &["Caio", "Ana"], &["Ribeiro", "Silva", "Costa"]),
        ],
        nicknames: (0..400).map(|n| format!("Nick{n}")).collect(),
        competitions: vec![Competition {
            id: id("competition:league"),
            region: id("region:up"),
            teams: teams.iter().map(|t| t.id.clone()).collect(),
        }],
        teams,
        players: Vec::new(),
        roles: roles(&CORE_WEIGHTS),
        roster: RosterRules { subs: 2 },
        generation: params(),
    }
}

fn pinned(slug: &str, team: &str, role: &str) -> PinnedPlayer {
    PinnedPlayer {
        id: id(&format!("player:{slug}")),
        team: id(&format!("team:{team}")),
        role: id(&format!("role:{role}")),
        nickname: None,
        given_name: None,
        family_name: None,
        nationality: None,
        birth_date: None,
        attributes: PinnedAttributes::default(),
    }
}

/// Every attribute that counts toward overall pinned at `points`.
fn flat(points: u32) -> PinnedAttributes {
    let r = Some(rating(points));
    PinnedAttributes {
        mechanics: r,
        laning: r,
        game_sense: r,
        awareness: r,
        positioning: r,
        champion_pool_breadth: r,
        shotcalling: r,
        teamwork: r,
        composure: r,
        ..PinnedAttributes::default()
    }
}

fn players_of<'a>(world: &'a World, team: &str) -> Vec<&'a Player> {
    let team = id(&format!("team:{team}"));
    world.players.iter().filter(|p| p.team == team).collect()
}

fn overall(world: &World, player: &Player) -> f64 {
    world.overall(player).unwrap().points()
}

fn mean(values: &[f64]) -> f64 {
    values.iter().sum::<f64>() / f64::from(u32::try_from(values.len()).unwrap())
}

fn std_dev(values: &[f64]) -> f64 {
    let m = mean(values);
    mean(&values.iter().map(|v| (v - m).powi(2)).collect::<Vec<_>>()).sqrt()
}

#[test]
fn same_template_and_seed_give_the_same_world() {
    // spec: GEN-001
    // Given
    let template = template(vec![team("a", "up", 70), team("b", "down", 40)]);
    // When
    let first = generate(template.clone(), &seed(42)).unwrap();
    let second = generate(template, &seed(42)).unwrap();
    // Then
    assert_eq!(first, second);
}

#[test]
fn a_different_seed_changes_the_players_not_the_structure() {
    // spec: GEN-002
    // Given
    let template = template(vec![team("a", "up", 70), team("b", "down", 40)]);
    // When
    let one = generate(template.clone(), &seed(1)).unwrap();
    let two = generate(template, &seed(2)).unwrap();
    // Then
    assert_eq!(
        (&one.regions, &one.competitions, &one.teams),
        (&two.regions, &two.competitions, &two.teams)
    );
    assert_ne!(one.players, two.players);
    let ids = |w: &World| w.players.iter().map(|p| p.id.clone()).collect::<Vec<_>>();
    assert_eq!(ids(&one), ids(&two));
}

#[test]
fn the_best_player_in_each_role_starts() {
    // spec: GEN-005
    // Given
    let mut template = template(vec![team("a", "up", 70)]);
    let mut strong = pinned("strong", "a", "mid");
    strong.attributes = flat(71);
    let mut weak = pinned("weak", "a", "mid");
    weak.attributes = flat(68);
    template.players = vec![weak, strong];
    // When
    let world = generate(template, &seed(7)).unwrap();
    // Then
    let mids: Vec<(&str, bool)> = players_of(&world, "a")
        .into_iter()
        .filter(|p| p.role == id("role:mid"))
        .map(|p| (p.id.slug(), p.starter))
        .collect();
    assert_eq!(mids, [("strong", true), ("weak", false)]);
}

#[test]
fn ties_for_a_starting_place_go_to_the_lower_id() {
    // spec: GEN-006
    // Given
    let mut template = template(vec![team("a", "up", 70)]);
    let mut b = pinned("b", "a", "support");
    b.attributes = flat(60);
    let mut a = pinned("a", "a", "support");
    a.attributes = flat(60);
    template.players = vec![b, a];
    // When
    let world = generate(template, &seed(7)).unwrap();
    // Then
    let starters: Vec<&str> = players_of(&world, "a")
        .into_iter()
        .filter(|p| p.role == id("role:support") && p.starter)
        .map(|p| p.id.slug())
        .collect();
    assert_eq!(starters, ["a"]);
}

#[test]
fn every_team_starts_exactly_one_player_per_role() {
    let template = template(vec![team("a", "up", 70), team("b", "down", 40)]);
    for value in 0..20 {
        let world = generate(template.clone(), &seed(value)).unwrap();
        for slug in ["a", "b"] {
            let mut starters: Vec<&str> = players_of(&world, slug)
                .into_iter()
                .filter(|p| p.starter)
                .map(|p| p.role.slug())
                .collect();
            starters.sort_unstable();
            assert_eq!(starters, ["bot", "jungle", "mid", "support", "top"]);
        }
    }
}

#[test]
fn higher_reputation_means_stronger_players() {
    // spec: GEN-007
    // Given
    let template = template(vec![team("strong", "up", 90), team("weak", "up", 30)]);
    // When
    let (mut strong, mut weak) = (Vec::new(), Vec::new());
    for value in 0..200 {
        let world = generate(template.clone(), &seed(value)).unwrap();
        strong.extend(
            players_of(&world, "strong")
                .into_iter()
                .map(|p| overall(&world, p)),
        );
        weak.extend(
            players_of(&world, "weak")
                .into_iter()
                .map(|p| overall(&world, p)),
        );
    }
    // Then
    assert!(
        mean(&strong) > mean(&weak) + 15.0,
        "{} vs {}",
        mean(&strong),
        mean(&weak)
    );
    assert!(
        std_dev(&strong) < std_dev(&weak),
        "{} vs {}",
        std_dev(&strong),
        std_dev(&weak)
    );
}

#[test]
fn the_region_level_shifts_every_team() {
    // spec: GEN-008
    // Given
    let template = template(vec![
        team("up_team", "up", 60),
        team("down_team", "down", 60),
    ]);
    // When
    let (mut up, mut down) = (Vec::new(), Vec::new());
    for value in 0..200 {
        let world = generate(template.clone(), &seed(value)).unwrap();
        up.extend(
            players_of(&world, "up_team")
                .into_iter()
                .map(|p| overall(&world, p)),
        );
        down.extend(
            players_of(&world, "down_team")
                .into_iter()
                .map(|p| overall(&world, p)),
        );
    }
    // Then
    let gap = mean(&up) - mean(&down);
    assert!((6.0..10.0).contains(&gap), "gap {gap}");
}

#[test]
fn a_role_shapes_the_attributes() {
    // spec: GEN-009
    // Given
    let template = template(vec![team("a", "up", 60), team("b", "up", 60)]);
    // When
    let (mut mid_mechanics, mut support_mechanics) = (Vec::new(), Vec::new());
    let (mut mid_calls, mut support_calls) = (Vec::new(), Vec::new());
    for value in 0..200 {
        let world = generate(template.clone(), &seed(value)).unwrap();
        for player in &world.players {
            let mechanics = player.attributes.skills.mechanics.points();
            let calls = player.attributes.skills.shotcalling.points();
            match player.role.slug() {
                "mid" => {
                    mid_mechanics.push(mechanics);
                    mid_calls.push(calls);
                }
                "support" => {
                    support_mechanics.push(mechanics);
                    support_calls.push(calls);
                }
                _ => {}
            }
        }
    }
    // Then
    assert!(mean(&mid_mechanics) > mean(&support_mechanics) + 5.0);
    assert!(mean(&support_calls) > mean(&mid_calls) + 5.0);
}

#[test]
fn nationalities_follow_the_regions_mix() {
    // spec: GEN-012
    // Given
    let template = template(vec![team("a", "up", 60), team("b", "up", 60)]);
    // When
    let (mut korean, mut total) = (0_u32, 0_u32);
    for value in 0..200 {
        let world = generate(template.clone(), &seed(value)).unwrap();
        for player in &world.players {
            total += 1;
            korean += u32::from(player.nationality == id("nationality:kr"));
        }
    }
    // Then
    let share = f64::from(korean) / f64::from(total);
    assert!((0.90..0.98).contains(&share), "share {share}");
}

#[test]
fn a_pinned_player_keeps_every_pinned_field() {
    // spec: GEN-015
    // Given
    let mut template = template(vec![team("a", "up", 70)]);
    let mut kairos = pinned("kairos", "a", "mid");
    kairos.nickname = Some("Kairos".to_owned());
    kairos.birth_date = Some("1997-03-14".parse().unwrap());
    kairos.attributes.mechanics = Some(rating(95));
    template.players = vec![kairos];
    // When
    let world = generate(template, &seed(3)).unwrap();
    // Then
    let kairos = world
        .players
        .iter()
        .find(|p| p.id == id("player:kairos"))
        .unwrap();
    assert_eq!(kairos.nickname, "Kairos");
    assert_eq!(kairos.role, id("role:mid"));
    assert_eq!(kairos.birth_date.to_string(), "1997-03-14");
    assert_eq!(kairos.attributes.skills.mechanics, rating(95));
    assert!(
        kairos.attributes.skills.laning >= Rating::MIN
            && kairos.attributes.skills.laning <= Rating::MAX
    );
    assert!(["Han", "Kim", "Ribeiro", "Silva", "Costa"].contains(&kairos.family_name.as_str()));
}

#[test]
fn pinned_names_nationality_and_every_attribute_are_kept() {
    let mut template = template(vec![team("a", "up", 70)]);
    let mut player = pinned("p", "a", "top");
    player.given_name = Some("Pinned".to_owned());
    player.family_name = Some("Person".to_owned());
    player.nationality = Some(id("nationality:br"));
    player.attributes = PinnedAttributes {
        aggression: Some(rating(11)),
        work_ethic: Some(rating(12)),
        consistency: Some(rating(13)),
        potential: Some(rating(14)),
        ..flat(80)
    };
    template.players = vec![player];
    let world = generate(template, &seed(3)).unwrap();
    let p = &world.players[0];
    assert_eq!(
        (p.given_name.as_str(), p.family_name.as_str()),
        ("Pinned", "Person")
    );
    assert_eq!(p.nationality, id("nationality:br"));
    let core = p.attributes.core;
    assert_eq!(
        [
            core.aggression,
            core.work_ethic,
            core.consistency,
            core.potential
        ],
        [rating(11), rating(12), rating(13), rating(14)]
    );
    for attribute in OverallAttribute::ALL {
        assert_eq!(p.attributes.get(attribute), rating(80), "{attribute:?}");
    }
}

#[test]
fn names_come_from_the_pinned_nationalitys_pool() {
    let mut template = template(vec![team("a", "up", 70)]);
    let mut player = pinned("p", "a", "top");
    player.nationality = Some(id("nationality:br"));
    template.players = vec![player];
    for value in 0..20 {
        let world = generate(template.clone(), &seed(value)).unwrap();
        let p = &world.players[0];
        assert!(["Caio", "Ana"].contains(&p.given_name.as_str()));
        assert!(["Ribeiro", "Silva", "Costa"].contains(&p.family_name.as_str()));
    }
}

#[test]
fn adding_a_team_leaves_the_others_alone() {
    // spec: GEN-016
    // Given
    let before = template(vec![team("a", "up", 70), team("c", "down", 40)]);
    let after = template(vec![
        team("a", "up", 70),
        team("b", "up", 55),
        team("c", "down", 40),
    ]);
    // When
    let one = generate(before, &seed(42)).unwrap();
    let two = generate(after, &seed(42)).unwrap();
    // Then
    let shape = |w: &World, slug: &str| {
        players_of(w, slug)
            .into_iter()
            .map(|p| {
                (
                    p.id.clone(),
                    p.attributes,
                    p.birth_date,
                    p.nationality.clone(),
                    p.given_name.clone(),
                    p.family_name.clone(),
                    p.nickname.clone(),
                )
            })
            .collect::<Vec<_>>()
    };
    assert_eq!(shape(&one, "a"), shape(&two, "a"));
    assert_eq!(shape(&one, "c"), shape(&two, "c"));
}

#[test]
fn pinning_a_field_shifts_no_other_draw() {
    let base = template(vec![team("a", "up", 70)]);
    let mut plain = base.clone();
    plain.players = vec![pinned("p", "a", "top")];
    let mut dated = base;
    let mut with_date = pinned("p", "a", "top");
    with_date.birth_date = Some("2003-05-05".parse().unwrap());
    dated.players = vec![with_date];
    let one = generate(plain, &seed(4)).unwrap();
    let two = generate(dated, &seed(4)).unwrap();
    let (a, b) = (&one.players[0], &two.players[0]);
    assert_eq!(
        (&a.given_name, &a.family_name, &a.nationality),
        (&b.given_name, &b.family_name, &b.nationality)
    );
    for attribute in OverallAttribute::ALL {
        assert_eq!(
            a.attributes.get(attribute),
            b.attributes.get(attribute),
            "{attribute:?}"
        );
    }
    assert_eq!(one.players[1..], two.players[1..]);
}

#[test]
fn how_pools_are_split_never_changes_the_world() {
    let joined = template(vec![team("a", "up", 70), team("b", "down", 40)]);
    let mut split = joined.clone();
    // The same names and nicknames, in other files and orders.
    let kr = split.name_pools.remove(0);
    split.name_pools.push(NamePool {
        given: vec![kr.given[2].clone()],
        family: vec![],
        ..kr.clone()
    });
    split.name_pools.push(NamePool {
        given: kr.given[..2].iter().rev().cloned().collect(),
        ..kr
    });
    split.nicknames.reverse();
    assert_eq!(
        generate(joined, &seed(8)).unwrap(),
        generate(split.clone(), &seed(8)).unwrap()
    );
}

#[test]
fn a_birth_date_after_the_start_is_an_error() {
    let mut template = template(vec![team("a", "up", 70)]);
    let mut late = pinned("late", "a", "top");
    late.birth_date = Some("2030-01-01".parse().unwrap());
    template.players = vec![late];
    assert_eq!(
        generate(template, &seed(1)),
        Err(GenerationError::BornAfterStart(id("player:late")))
    );
}

#[test]
fn a_pinned_player_on_no_team_is_an_error() {
    let mut template = template(vec![team("a", "up", 70)]);
    template.players = vec![pinned("p", "nowhere", "top")];
    assert_eq!(
        generate(template, &seed(1)),
        Err(GenerationError::Unknown(id("team:nowhere")))
    );
}

#[test]
fn potential_is_never_below_current_ability() {
    // spec: GEN-017
    // Given
    let template = template(vec![team("a", "up", 95), team("b", "down", 20)]);
    for value in 0..50 {
        // When
        let world = generate(template.clone(), &seed(value)).unwrap();
        // Then
        for player in &world.players {
            assert!(player.attributes.core.potential >= world.overall(player).unwrap());
        }
    }
}

#[test]
fn a_pinned_potential_may_sit_below_current_ability() {
    let mut template = template(vec![team("a", "up", 70)]);
    let mut veteran = pinned("veteran", "a", "top");
    veteran.attributes = PinnedAttributes {
        potential: Some(rating(40)),
        ..flat(80)
    };
    template.players = vec![veteran];
    let world = generate(template, &seed(1)).unwrap();
    assert_eq!(world.players[0].attributes.core.potential, rating(40));
}

#[test]
fn young_players_have_more_room_to_grow() {
    let template = template(vec![team("a", "up", 60), team("b", "up", 60)]);
    let start = template.settings.start_date;
    let (mut young, mut old) = (Vec::new(), Vec::new());
    for value in 0..200 {
        let world = generate(template.clone(), &seed(value)).unwrap();
        for player in &world.players {
            let room = player.attributes.core.potential.points() - overall(&world, player);
            match player.birth_date.age_on(start).unwrap() {
                ..=19 => young.push(room),
                25.. => old.push(room),
                _ => {}
            }
        }
    }
    assert!(
        mean(&young) > mean(&old) + 5.0,
        "{} vs {}",
        mean(&young),
        mean(&old)
    );
}

#[test]
fn the_roster_shape_follows_the_role_set() {
    // spec: GEN-019
    // Given
    let mut template = template(vec![team("a", "up", 60), team("b", "down", 50)]);
    template.roles = roles(&CORE_WEIGHTS[..3]);
    template.roster = RosterRules { subs: 1 };
    // When
    let world = generate(template, &seed(9)).unwrap();
    // Then
    for slug in ["a", "b"] {
        let players = players_of(&world, slug);
        assert_eq!(players.len(), 4);
        let mut roles: Vec<&str> = players.iter().map(|p| p.role.slug()).collect();
        roles.sort_unstable();
        roles.dedup();
        assert_eq!(roles, ["jungle", "mid", "top"]);
    }
}

#[test]
fn rosters_have_every_role_and_subs_in_different_roles() {
    let template = template(vec![team("a", "up", 60), team("b", "down", 50)]);
    for value in 0..50 {
        let world = generate(template.clone(), &seed(value)).unwrap();
        for slug in ["a", "b"] {
            let mut counts: BTreeMap<&str, usize> = BTreeMap::new();
            for player in players_of(&world, slug) {
                *counts.entry(player.role.slug()).or_default() += 1;
            }
            assert_eq!(counts.len(), 5);
            assert_eq!(counts.values().sum::<usize>(), 7);
            assert_eq!(counts.values().filter(|&&c| c == 2).count(), 2);
        }
    }
}

#[test]
fn generated_ids_number_the_teams_slots() {
    let mut template = template(vec![team("a", "up", 60)]);
    template.players = vec![pinned("star", "a", "mid")];
    let world = generate(template, &seed(1)).unwrap();
    let ids: Vec<&str> = world.players.iter().map(|p| p.id.as_str()).collect();
    assert_eq!(
        ids,
        [
            "player:star",
            "player:a.1",
            "player:a.2",
            "player:a.3",
            "player:a.4",
            "player:a.5",
            "player:a.6"
        ]
    );
    assert!(world.players[1..].iter().all(|p| p.id.is_generated()));
}

#[test]
fn nicknames_are_unique_and_pinned_ones_are_reserved() {
    let mut template = template(vec![
        team("a", "up", 60),
        team("b", "up", 60),
        team("c", "down", 40),
    ]);
    template.nicknames = (0..25).map(|n| format!("Nick{n}")).collect();
    let mut star = pinned("star", "a", "mid");
    star.nickname = Some("nick3".to_owned());
    template.players = vec![star];
    let world = generate(template, &seed(5)).unwrap();
    let mut seen: Vec<String> = world
        .players
        .iter()
        .map(|p| p.nickname.to_lowercase())
        .collect();
    assert_eq!(world.players[0].nickname, "nick3");
    seen.sort();
    seen.dedup();
    assert_eq!(seen.len(), 21);
}

#[test]
fn ages_and_birth_dates_agree() {
    let template = template(vec![team("a", "up", 60), team("b", "down", 50)]);
    let start = template.settings.start_date;
    let mut ages = std::collections::BTreeSet::new();
    for value in 0..100 {
        let world = generate(template.clone(), &seed(value)).unwrap();
        for player in &world.players {
            let age = player.birth_date.age_on(start).unwrap();
            assert!((17..=28).contains(&age), "{age}");
            ages.insert(age);
        }
    }
    assert!(ages.contains(&17) && ages.contains(&28) && ages.contains(&22));
}

#[test]
fn birth_dates_cover_the_whole_year_of_an_age() {
    let mut template = template(vec![team("a", "up", 60)]);
    template.generation.common.age_min = 20;
    template.generation.common.age_max = 20;
    let start = template.settings.start_date;
    let (mut earliest, mut latest) = (start, start.years_before(30).unwrap());
    for value in 0..300 {
        for player in generate(template.clone(), &seed(value)).unwrap().players {
            earliest = earliest.min(player.birth_date);
            latest = latest.max(player.birth_date);
        }
    }
    assert_eq!(earliest.to_string(), "2006-01-02");
    assert_eq!(latest.to_string(), "2007-01-01");
}

#[test]
fn templates_built_by_hand_report_what_is_wrong() {
    let mut unknown_region = template(vec![team("a", "nowhere", 60)]);
    assert_eq!(
        generate(unknown_region.clone(), &seed(1)),
        Err(GenerationError::Unknown(id("region:nowhere")))
    );
    unknown_region.teams = vec![team("a", "up", 60)];
    unknown_region.players = vec![pinned("p", "a", "coach")];
    assert_eq!(
        generate(unknown_region, &seed(1)),
        Err(GenerationError::Unknown(id("role:coach")))
    );

    let mut empty_mix = template(vec![team("a", "up", 60)]);
    empty_mix.regions[0].nationalities = vec![(id("nationality:kr"), 0)];
    assert_eq!(
        generate(empty_mix.clone(), &seed(1)),
        Err(GenerationError::EmptyMix(id("region:up")))
    );

    let mut no_names = template(vec![team("a", "down", 60)]);
    no_names
        .name_pools
        .retain(|pool| pool.nationality != id("nationality:br"));
    assert_eq!(
        generate(no_names.clone(), &seed(1)),
        Err(GenerationError::EmptyNames(id("nationality:br")))
    );

    let mut empty_given = template(vec![team("a", "down", 60)]);
    empty_given.name_pools[1].given.clear();
    assert_eq!(
        generate(empty_given.clone(), &seed(1)),
        Err(GenerationError::EmptyNames(id("nationality:br")))
    );
    let mut empty_family = template(vec![team("a", "down", 60)]);
    empty_family.name_pools[1].family.clear();
    assert_eq!(
        generate(empty_family.clone(), &seed(1)),
        Err(GenerationError::EmptyNames(id("nationality:br")))
    );

    let mut crowded = template(vec![team("a", "up", 60)]);
    crowded.players = (0..3)
        .map(|n| pinned(&format!("p{n}"), "a", "mid"))
        .collect();
    assert_eq!(
        generate(crowded, &seed(1)),
        Err(GenerationError::IncompletableRoster(id("team:a")))
    );

    let mut cornered = template(vec![team("a", "up", 60)]);
    cornered.players = ["top", "top", "mid", "mid", "bot", "bot"]
        .iter()
        .enumerate()
        .map(|(n, role)| pinned(&format!("p{n}"), "a", role))
        .collect();
    assert_eq!(
        generate(cornered, &seed(1)),
        Err(GenerationError::IncompletableRoster(id("team:a")))
    );

    let mut overfull = template(vec![team("a", "up", 60)]);
    overfull.players = [
        "top", "top", "mid", "mid", "bot", "jungle", "support", "support",
    ]
    .iter()
    .enumerate()
    .map(|(n, role)| pinned(&format!("p{n}"), "a", role))
    .collect();
    assert_eq!(
        generate(overfull, &seed(1)),
        Err(GenerationError::IncompletableRoster(id("team:a")))
    );

    let mut few_nicknames = template(vec![team("a", "up", 60)]);
    few_nicknames.nicknames.truncate(6);
    assert_eq!(
        generate(few_nicknames.clone(), &seed(1)),
        Err(GenerationError::NicknamesExhausted)
    );
}

#[test]
fn every_skill_is_drawn_independently() {
    let template = template(vec![team("a", "up", 60)]);
    let world = generate(template, &seed(11)).unwrap();
    for player in &world.players {
        let skills: std::collections::BTreeSet<Rating> = MobaSkill::ALL
            .iter()
            .map(|&s| player.attributes.skills.get(s))
            .collect();
        assert!(skills.len() > 3, "{:?}", player.attributes.skills);
    }
}

#[test]
fn potential_adds_room_for_each_year_under_the_peak() {
    let mut template = template(vec![team("a", "up", 70)]);
    template.generation.common.potential_spread = 0.0;
    let mut young = pinned("young", "a", "top");
    young.birth_date = Some("2006-06-01".parse().unwrap());
    young.attributes = flat(60);
    template.players = vec![young];
    let world = generate(template, &seed(1)).unwrap();
    // Age 20, four years under 24: 60 + 2.5 × 4.
    assert_eq!(world.players[0].attributes.core.potential, rating(70));
}

#[test]
fn starters_are_the_highest_overall_then_the_lowest_id() {
    let template = template(vec![team("a", "up", 70)]);
    let player = |slug: &str, points: u32| Player {
        id: id(&format!("player:{slug}")),
        team: id("team:a"),
        role: id("role:mid"),
        starter: false,
        nickname: String::new(),
        given_name: String::new(),
        family_name: String::new(),
        nationality: id("nationality:kr"),
        birth_date: "2000-01-01".parse().unwrap(),
        attributes: crate::moba::attributes::MobaAttributes::uniform(rating(points)),
    };
    let starter = |mut players: Vec<Player>| {
        pick_starters(&template, &mut players);
        players
            .into_iter()
            .filter(|p| p.starter)
            .map(|p| p.id.slug().to_owned())
            .collect::<Vec<_>>()
    };
    assert_eq!(starter(vec![player("z", 60), player("a", 60)]), ["a"]);
    assert_eq!(starter(vec![player("a", 60), player("z", 60)]), ["a"]);
    assert_eq!(starter(vec![player("a", 50), player("z", 60)]), ["z"]);
    assert_eq!(starter(vec![player("z", 60), player("a", 50)]), ["z"]);
}

/// Pins the generator's exact output for a small template, so any change to
/// a draw, its order or its arithmetic is deliberate. Saves made from the
/// same seed and packages depend on it.
#[test]
fn the_generated_world_is_pinned() {
    use std::fmt::Write;
    let world = generate(
        template(vec![team("a", "up", 70), team("b", "down", 40)]),
        &seed(42),
    )
    .unwrap();
    let mut text = String::new();
    for p in &world.players {
        let a = &p.attributes;
        let skills: Vec<u16> = MobaSkill::ALL
            .iter()
            .map(|&s| a.skills.get(s).hundredths())
            .collect();
        let core = [
            a.core.teamwork,
            a.core.aggression,
            a.core.composure,
            a.core.work_ethic,
            a.core.consistency,
            a.core.potential,
        ]
        .map(Rating::hundredths);
        writeln!(
            text,
            "{} {} {} {} {} {} {} {skills:?} {core:?}",
            p.id, p.role, p.starter, p.nickname, p.given_name, p.family_name, p.birth_date
        )
        .unwrap();
    }
    assert_eq!(text, PINNED_WORLD);
}

const PINNED_WORLD: &str = "\
player:a.1 role:top true Nick173 Ha-eun Han 2007-04-25 [7232, 8669, 6819, 6960, 6947, 5982, 6901] [6140, 5215, 6519, 3083, 7123, 8335]\n\
player:a.2 role:jungle false Nick75 Ha-eun Kim 2006-01-29 [6904, 6955, 7829, 8092, 7059, 6921, 7436] [6637, 4626, 7118, 3754, 6044, 9192]\n\
player:a.3 role:mid true Nick132 Ha-eun Han 2007-04-20 [7108, 6984, 7544, 6755, 6944, 6254, 7689] [6580, 5254, 7897, 5789, 5107, 8340]\n\
player:a.4 role:bot true Nick193 Ha-eun Kim 2002-12-07 [9245, 8725, 8266, 8450, 8522, 8403, 7223] [8026, 7129, 8249, 6719, 3359, 8550]\n\
player:a.5 role:support false Nick244 Ha-eun Kim 2003-10-05 [5386, 4550, 5491, 5637, 5351, 4233, 5856] [5358, 3654, 4529, 3511, 2395, 5980]\n\
player:a.6 role:jungle true Nick168 Ha-eun Han 2003-11-16 [7125, 6644, 7713, 7363, 7618, 6542, 7848] [6763, 3868, 7788, 3744, 3812, 7370]\n\
player:a.7 role:support true Nick245 Do-yun Han 2001-09-17 [6404, 5489, 5648, 6635, 6413, 5899, 4747] [6277, 7360, 4453, 4912, 5540, 6144]\n\
player:b.1 role:top true Nick15 Caio Ribeiro 2006-02-05 [5032, 5796, 5957, 5241, 5396, 4043, 4986] [4687, 5146, 5348, 4687, 5776, 7435]\n\
player:b.2 role:jungle true Nick207 Caio Silva 2004-07-25 [4944, 4051, 4973, 4719, 5128, 5316, 6371] [4791, 5562, 4065, 5407, 3543, 5016]\n\
player:b.3 role:mid false Nick29 Ana Ribeiro 2003-11-10 [4449, 3185, 3064, 3451, 2403, 3371, 3019] [2870, 5882, 2436, 6646, 4674, 3549]\n\
player:b.4 role:bot true Nick191 Caio Costa 2005-01-25 [4301, 6990, 4500, 5065, 5253, 5067, 4953] [4483, 7889, 4805, 2812, 5639, 5839]\n\
player:b.5 role:support true Nick147 Ana Ribeiro 2008-06-30 [4164, 4242, 4619, 3610, 3691, 3730, 4700] [3989, 3775, 4317, 5473, 4554, 5546]\n\
player:b.6 role:mid true Nick9 Caio Costa 2005-04-27 [5040, 5141, 3842, 4338, 3764, 2723, 4377] [3152, 3399, 3678, 1837, 3105, 5492]\n\
player:b.7 role:bot false Nick339 Ana Silva 2004-10-17 [4482, 3483, 3080, 4803, 4113, 2927, 4295] [3399, 4848, 3600, 2776, 5916, 4562]\n\
";
