// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! The core package through the generator: the scenarios that hold for any
//! world built from it, and the snapshot that must match on every OS.

#![allow(
    clippy::unwrap_used,
    reason = "helpers of an integration test, which may panic"
)]

use std::collections::BTreeSet;
use std::fmt::Write;
use std::path::Path;

use app::rng::RngProvider;
use domain::rating::Rating;
use domain::rng::WorldSeed;
use esports::moba::attributes::{MobaSkill, OverallAttribute};
use esports::moba::generation::generate;
use esports::moba::world::World;
use sha2::{Digest, Sha256};

fn core() -> packages::Package {
    packages::load(&Path::new(env!("CARGO_MANIFEST_DIR")).join("../../content/core")).unwrap()
}

fn world(seed: u64) -> World {
    generate(core().template, &RngProvider::new(WorldSeed::new(seed))).unwrap()
}

/// Every field of every player, one line each.
fn dump(world: &World) -> String {
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
            "{} {} {} {} {}|{}|{} {} {} {skills:?} {core:?}",
            p.id,
            p.team,
            p.role,
            p.starter,
            p.nickname,
            p.given_name,
            p.family_name,
            p.nationality,
            p.birth_date
        )
        .unwrap();
    }
    text
}

#[test]
fn the_same_world_on_every_operating_system() {
    // spec: GEN-003
    // Given
    let seed = 42;
    // When
    let text = dump(&world(seed));
    // Then
    let hash = Sha256::digest(text.as_bytes())
        .iter()
        .fold(String::new(), |mut hex, byte| {
            let _ = write!(hex, "{byte:02x}");
            hex
        });
    assert_eq!(
        hash, "a57b29a35a37d2d6be1962c94a882c04686655db939d4100ea18071067c20de1",
        "the core world for seed 42 changed:\n{text}"
    );
}

#[test]
fn every_roster_has_the_right_shape() {
    // spec: GEN-004
    // Given
    let world = world(7);
    // When
    for team in &world.teams {
        let roles: Vec<&str> = world
            .players
            .iter()
            .filter(|p| p.team == team.id)
            .map(|p| p.role.slug())
            .collect();
        // Then
        let distinct: BTreeSet<&str> = roles.iter().copied().collect();
        assert_eq!(roles.len(), 7, "{}", team.id);
        assert_eq!(distinct.len(), 5, "{}", team.id);
        let doubled = distinct
            .iter()
            .filter(|r| roles.iter().filter(|x| x == r).count() == 2)
            .count();
        assert_eq!(doubled, 2, "{}", team.id);
    }
    assert_eq!(world.players.len(), 18 * 7);
}

#[test]
fn ratings_stay_in_range_at_hundredths() {
    // spec: GEN-010
    // Given
    let world = world(7);
    // When
    for player in &world.players {
        let a = &player.attributes;
        let ratings = OverallAttribute::ALL
            .map(|attribute| a.get(attribute))
            .into_iter()
            .chain([
                a.core.aggression,
                a.core.work_ethic,
                a.core.consistency,
                a.core.potential,
            ]);
        // Then
        for rating in ratings {
            assert!((100..=9900).contains(&rating.hundredths()));
        }
    }
}

#[test]
fn ages_and_birth_dates_agree() {
    // spec: GEN-011
    // Given
    let package = core();
    let pinned: BTreeSet<_> = package
        .template
        .players
        .iter()
        .filter(|p| p.birth_date.is_some())
        .map(|p| p.id.clone())
        .collect();
    let start = package.template.settings.start_date;
    // When
    let world = world(7);
    // Then
    for player in world.players.iter().filter(|p| !pinned.contains(&p.id)) {
        let age = player.birth_date.age_on(start).unwrap();
        assert!((17..=28).contains(&age), "{} is {age}", player.id);
    }
}

#[test]
fn names_come_from_the_nationalitys_pools() {
    // spec: GEN-013
    // Given
    let package = core();
    let pinned: BTreeSet<_> = package
        .template
        .players
        .iter()
        .map(|p| p.id.clone())
        .collect();
    // When
    let world = world(7);
    // Then
    for player in world.players.iter().filter(|p| !pinned.contains(&p.id)) {
        let pools: Vec<_> = package
            .template
            .name_pools
            .iter()
            .filter(|pool| pool.nationality == player.nationality)
            .collect();
        assert!(
            pools
                .iter()
                .any(|pool| pool.given.contains(&player.given_name)),
            "{}",
            player.id
        );
        assert!(
            pools
                .iter()
                .any(|pool| pool.family.contains(&player.family_name)),
            "{}",
            player.id
        );
    }
}

#[test]
fn nicknames_are_unique() {
    // spec: GEN-014
    // Given
    let world = world(7);
    // When
    let distinct: BTreeSet<String> = world
        .players
        .iter()
        .map(|p| p.nickname.to_lowercase())
        .collect();
    // Then
    assert_eq!(distinct.len(), world.players.len());
}

#[test]
fn the_special_players_are_where_the_package_put_them() {
    let world = world(7);
    let find = |slug: &str| world.players.iter().find(|p| p.id.slug() == slug).unwrap();
    let kairos = find("kairos");
    assert_eq!(
        (
            kairos.nickname.as_str(),
            kairos.team.slug(),
            kairos.role.slug()
        ),
        ("Kairos", "azure_tigers", "mid")
    );
    assert!(kairos.starter, "a 95-97 mid starts");
    assert_eq!(find("faisca").attributes.core.potential.display(), 94);
    assert_eq!(find("wildfire").attributes.core.consistency.display(), 25);
}

#[test]
#[ignore = "prints a summary of the core world for eyeballing"]
fn print_summary() {
    let world = world(42);
    for team in &world.teams {
        let players: Vec<_> = world.players.iter().filter(|p| p.team == team.id).collect();
        let overalls: Vec<u8> = players
            .iter()
            .map(|p| world.overall(p).unwrap().display())
            .collect();
        println!(
            "{:<22} rep {:>3}  {:?}",
            team.id.slug(),
            team.reputation.value(),
            overalls
        );
    }
    for p in world.players.iter().filter(|p| !p.id.is_generated()) {
        println!(
            "{} {} {} overall {} potential {}",
            p.nickname,
            p.given_name,
            p.family_name,
            world.overall(p).unwrap().display(),
            p.attributes.core.potential.display()
        );
    }
}

#[test]
fn every_crests_text_is_readable() {
    // spec: ROST-010
    // Given every team in the core package
    for team in &core().template.teams {
        // When its crest is built
        let crest = app::views::Crest::of(team);
        // Then the text reaches 4.5:1 against the fill
        let fill = domain::world::Colour::parse(&crest.fill).unwrap();
        let text = domain::world::Colour::parse(&crest.text).unwrap();
        assert!(
            fill.contrast(text) >= 4.5,
            "{}: {:.2}",
            team.id,
            fill.contrast(text)
        );
    }
}
