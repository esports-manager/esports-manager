// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

use rand_chacha::ChaCha8Rng;
use rand_core::{Rng, SeedableRng};

use super::*;
use crate::random::normal;

fn stream(seed: u64) -> ChaCha8Rng {
    ChaCha8Rng::seed_from_u64(seed)
}

fn id(text: &str) -> ContentId {
    ContentId::parse(text).unwrap()
}

/// The core package's constants.
fn constants() -> Constants {
    Constants {
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
    }
}

fn reputation(value: u32) -> Reputation {
    Reputation::new(value).unwrap()
}

/// Whether `a` and `b` are at the same point in their streams.
fn in_step(mut a: ChaCha8Rng, mut b: ChaCha8Rng) -> bool {
    a.next_u64() == b.next_u64()
}

#[test]
fn strength_follows_reputation_and_region() {
    let c = constants();
    assert_eq!(
        Strength::of(&c, reputation(50), 4),
        Strength {
            mu: 59.0,
            sigma: 8.5
        }
    );
    let top = Strength::of(&c, reputation(100), -4);
    assert!(
        (top.mu - 71.0).abs() < 1e-9 && (top.sigma - 5.0).abs() < 1e-9,
        "{top:?}"
    );
    // The spread never goes below its floor.
    let steep = Constants {
        sigma_per_reputation: 1.0,
        ..c
    };
    assert_eq!(Strength::of(&steep, reputation(100), 0).sigma, 2.0);
}

#[test]
fn team_strength_follows_the_spec_table() {
    let c = constants();
    let cases = [
        (95, 4, 77.0, 5.35),
        (35, 4, 53.0, 9.55),
        (85, -4, 65.0, 6.05),
        (30, -4, 43.0, 9.9),
        (100, 0, 75.0, 5.0),
    ];
    for (value, level, mu, sigma) in cases {
        let strength = Strength::of(&c, reputation(value), level);
        assert!((strength.mu - mu).abs() < 1e-9, "{value}: {}", strength.mu);
        assert!(
            (strength.sigma - sigma).abs() < 1e-9,
            "{value}: {}",
            strength.sigma
        );
    }
    let floor = Constants {
        sigma_min: 6.0,
        ..c
    };
    assert!((Strength::of(&floor, reputation(95), 0).sigma - 6.0).abs() < 1e-9);
}

#[test]
fn a_birth_date_gives_exactly_the_drawn_age() {
    let start: GameDate = "2027-01-01".parse().unwrap();
    let fixed = Constants {
        age_min: 20,
        age_max: 20,
        ..constants()
    };
    let (mut earliest, mut latest) = (GameDate::MAX, GameDate::MIN);
    for seed in 0..4000 {
        let born = birth_date(&mut stream(seed), &fixed, start);
        assert_eq!(born.age_on(start), Some(20), "{born}");
        earliest = earliest.min(born);
        latest = latest.max(born);
    }
    // The draw covers the whole window: born 2006-01-02 to 2007-01-01.
    assert_eq!(earliest, "2006-01-02".parse().unwrap());
    assert_eq!(latest, "2007-01-01".parse().unwrap());
    let ages: BTreeSet<u16> = (0..400)
        .map(|seed| birth_date(&mut stream(seed), &constants(), start))
        .map(|born| born.age_on(start).unwrap())
        .collect();
    assert_eq!(ages.first(), Some(&17));
    assert_eq!(ages.last(), Some(&28));
}

#[test]
fn a_birth_date_draws_two_values() {
    let start: GameDate = "2027-01-01".parse().unwrap();
    let (mut drawn, mut by_hand) = (stream(7), stream(7));
    birth_date(&mut drawn, &constants(), start);
    normal(&mut by_hand, 0.0, 1.0);
    below(&mut by_hand, 365).unwrap();
    assert!(in_step(drawn, by_hand));
}

fn region(mix: &[(&str, u32)]) -> Region {
    Region {
        id: id("region:r"),
        level: 0,
        nationalities: mix.iter().map(|&(n, w)| (id(n), w)).collect(),
    }
}

fn pool(nationality: &str, given: &[&str], family: &[&str]) -> NamePool {
    NamePool {
        nationality: id(nationality),
        given: given.iter().map(|&s| s.to_owned()).collect(),
        family: family.iter().map(|&s| s.to_owned()).collect(),
    }
}

#[test]
fn names_come_from_the_drawn_nationality_and_pools_merge_sorted() {
    // Two files for one nationality, in either order, are one pool.
    let split = [
        pool("nationality:kr", &["Min", "Ji"], &["Kim"]),
        pool("nationality:kr", &["Ji", "Ara"], &["Lee"]),
    ];
    let swapped = [split[1].clone(), split[0].clone()];
    let only_kr = region(&[("nationality:kr", 1)]);
    for seed in 0..50 {
        let a = NamePools::new(&split).draw(&mut stream(seed), &only_kr, None);
        let b = NamePools::new(&swapped).draw(&mut stream(seed), &only_kr, None);
        assert_eq!(a, b);
        let identity = a.unwrap();
        assert_eq!(identity.nationality, id("nationality:kr"));
        assert!(["Ara", "Ji", "Min"].contains(&identity.given_name.as_str()));
        assert!(["Kim", "Lee"].contains(&identity.family_name.as_str()));
    }
}

#[test]
fn a_pinned_nationality_replaces_the_drawn_one_after_the_same_draws() {
    let pools = [
        pool("nationality:kr", &["Min"], &["Kim"]),
        pool("nationality:br", &["Caio"], &["Silva"]),
    ];
    let names = NamePools::new(&pools);
    let only_kr = region(&[("nationality:kr", 1)]);
    let (mut pinned, mut drawn) = (stream(3), stream(3));
    let identity = names
        .draw(&mut pinned, &only_kr, Some(&id("nationality:br")))
        .unwrap();
    assert_eq!(
        identity,
        Identity {
            nationality: id("nationality:br"),
            given_name: "Caio".into(),
            family_name: "Silva".into(),
        }
    );
    names.draw(&mut drawn, &only_kr, None).unwrap();
    assert!(in_step(pinned, drawn), "pinning shifts no later draw");
}

#[test]
fn empty_mixes_and_pools_are_errors() {
    let pools = [pool("nationality:kr", &["Min"], &[])];
    let names = NamePools::new(&pools);
    assert_eq!(
        names.draw(&mut stream(1), &region(&[]), None),
        Err(DrawError::EmptyMix(id("region:r")))
    );
    assert_eq!(
        names.draw(&mut stream(1), &region(&[("nationality:kr", 1)]), None),
        Err(DrawError::EmptyNames(id("nationality:kr")))
    );
    assert_eq!(
        names.draw(&mut stream(1), &region(&[("nationality:se", 1)]), None),
        Err(DrawError::EmptyNames(id("nationality:se")))
    );
}

#[test]
fn traits_are_four_normal_draws_in_order() {
    let c = constants();
    let (mut drawn, mut by_hand) = (stream(9), stream(9));
    let traits = Traits::draw(&mut drawn, &c);
    let expected = Traits {
        aggression: Rating::clamped(normal(&mut by_hand, 50.0, 15.0)),
        work_ethic: Rating::clamped(normal(&mut by_hand, 50.0, 15.0)),
        consistency: Rating::clamped(normal(&mut by_hand, 55.0, 15.0)),
        potential_noise: normal(&mut by_hand, 0.0, 6.0),
    };
    assert_eq!(traits, expected);
    assert!(in_step(drawn, by_hand));
}

#[test]
fn potential_grows_with_youth_and_never_falls_below_overall() {
    let c = constants();
    let points = |rating: Rating| rating.points();
    // 4 years under the peak age: +10.
    assert_eq!(points(potential(&c, 70.0, 20, 0.0)), 80.0);
    assert_eq!(points(potential(&c, 70.0, 20, 1.5)), 81.5);
    // At or past the peak, only the noise is left, and never below overall.
    assert_eq!(points(potential(&c, 70.0, 24, 2.0)), 72.0);
    assert_eq!(points(potential(&c, 70.0, 30, -5.0)), 70.0);
    // Clamped to a rating.
    assert_eq!(points(potential(&c, 95.0, 17, 6.0)), 99.0);
}

fn nicknames(names: &[&str]) -> Vec<String> {
    names.iter().map(|&s| s.to_owned()).collect()
}

#[test]
fn nicknames_are_unique_ignoring_case_and_skip_pinned_ones() {
    let pool = nicknames(&["Ace", "ace", "Blaze", "Kairos", "Dusk"]);
    let mut taken = Nicknames::new(&pool, ["KAIROS"]);
    let mut rng = stream(5);
    let mut drawn: Vec<&str> = (0..3).map(|_| taken.draw(&mut rng).unwrap()).collect();
    drawn.sort_unstable();
    // "Ace" and "ace" are one entry, and the pinned "Kairos" is already taken.
    assert_eq!(drawn, ["Ace", "Blaze", "Dusk"]);
    assert_eq!(taken.draw(&mut rng), None);
}

#[test]
fn how_the_pool_is_ordered_never_matters() {
    let a = nicknames(&["Dusk", "Ace", "Blaze", "Comet"]);
    let b = nicknames(&["Comet", "Blaze", "Ace", "Dusk"]);
    for seed in 0..20 {
        let draw = |pool: &[String]| {
            let mut names = Nicknames::new(pool, []);
            let mut rng = stream(seed);
            (0..3)
                .map(|_| names.draw(&mut rng).unwrap().to_owned())
                .collect::<Vec<_>>()
        };
        assert_eq!(draw(&a), draw(&b));
    }
}

#[test]
fn a_nickname_changes_only_when_another_player_took_it() {
    let pool = nicknames(&["Ace", "Blaze", "Comet", "Dusk", "Echo", "Flint"]);
    // A player's first draw, alone in the world.
    let alone = Nicknames::new(&pool, []).draw(&mut stream(11)).unwrap();
    // Another player took a different nickname first: no change.
    let other = pool.iter().find(|n| *n != alone).unwrap();
    let mut world = Nicknames::new(&pool, [other.as_str()]);
    assert_eq!(world.draw(&mut stream(11)), Some(alone));
    // Another took the very one: the player redraws something else.
    let mut world = Nicknames::new(&pool, [alone]);
    let redrawn = world.draw(&mut stream(11)).unwrap();
    assert_ne!(redrawn, alone);
}

#[test]
fn after_every_try_hits_a_taken_nickname_the_free_one_is_found() {
    // One free entry in a large pool: redraws almost surely all hit taken
    // ones, so the fallback picks the only free entry.
    let pool: Vec<String> = (0..1000).map(|n| format!("N{n:04}")).collect();
    let taken: Vec<&str> = pool.iter().skip(1).map(String::as_str).collect();
    let mut names = Nicknames::new(&pool, taken);
    assert_eq!(names.draw(&mut stream(2)), Some("N0000"));
    assert_eq!(names.draw(&mut stream(2)), None);
}
