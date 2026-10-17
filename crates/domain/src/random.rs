// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Draws from a random stream (ADR 0003).
//!
//! Domain code receives a stream and never creates one. Every draw here gives
//! the same result on every OS: integers are exact, and the normal draw uses
//! the pure-Rust `libm` functions instead of the platform's maths library,
//! which can differ in the last bit between systems.

use rand_core::Rng;

/// 2⁻⁵³: the spacing of the 53-bit grid that unit draws land on.
const UNIT_STEP: f64 = 1.0 / 9_007_199_254_740_992.0;

/// A uniform float in (0, 1], on a grid of 2⁵³ evenly spaced values.
/// Zero is excluded so the result can go into a logarithm.
pub fn unit(rng: &mut impl Rng) -> f64 {
    let bits = (rng.next_u64() >> 11) + 1;
    #[expect(
        clippy::cast_precision_loss,
        reason = "bits is at most 2^53, which an f64 represents exactly"
    )]
    let exact = bits as f64;
    exact * UNIT_STEP
}

/// A draw from the normal distribution N(`mean`, `std_dev`²), by Box–Muller.
/// Each draw takes two values from the stream.
pub fn normal(rng: &mut impl Rng, mean: f64, std_dev: f64) -> f64 {
    let radius = libm::sqrt(-2.0 * libm::log(unit(rng)));
    let angle = std::f64::consts::TAU * unit(rng);
    mean + std_dev * radius * libm::cos(angle)
}

/// Rounds `value` to the nearest integer, ties away from zero, and clamps it
/// to `min..=max`. A NaN becomes `min`, and so does any value when the range
/// is empty (`min > max`).
#[must_use]
pub fn round_clamped(value: f64, min: i32, max: i32) -> i32 {
    let rounded = value.round();
    if rounded.is_nan() {
        return min;
    }
    // An empty range clamps to `min..=min`.
    let bounded = rounded.clamp(f64::from(min), f64::from(max.max(min)));
    #[expect(
        clippy::cast_possible_truncation,
        reason = "rounded and clamped to an i32 range just above"
    )]
    let whole = bounded as i32;
    whole
}

/// A uniform index into `0..len` that `taken` doesn't hold. Entries of
/// `taken` at `len` or beyond are ignored. `None` when every index is taken.
pub fn index_excluding(
    rng: &mut impl Rng,
    len: usize,
    taken: &std::collections::BTreeSet<usize>,
) -> Option<usize> {
    let free = len.checked_sub(taken.range(..len).count())?;
    let mut choice = index(rng, free)?;
    for &used in taken.range(..len) {
        if used <= choice {
            choice += 1;
        } else {
            break;
        }
    }
    Some(choice)
}

/// Redraws allowed before `below` accepts a biased value. A redraw happens
/// with probability under `bound / 2⁶⁴`, so for any bound the game uses,
/// reaching the limit is less likely than 2⁻²⁰⁴⁸. The limit only keeps the
/// loop finite.
const MAX_ATTEMPTS: u32 = 64;

/// A uniform integer in `0..bound`, with no modulo bias. `None` when `bound`
/// is zero.
pub fn below(rng: &mut impl Rng, bound: u64) -> Option<u64> {
    if bound == 0 {
        return None;
    }
    // Values under `threshold` would make the low results more likely.
    let threshold = bound.wrapping_neg() % bound;
    let mut value = rng.next_u64();
    for _ in 1..MAX_ATTEMPTS {
        if value >= threshold {
            break;
        }
        value = rng.next_u64();
    }
    Some(value % bound)
}

/// A uniform index into a collection of `len` items. `None` when it is empty.
pub fn index(rng: &mut impl Rng, len: usize) -> Option<usize> {
    let bound = u64::try_from(len).ok()?;
    usize::try_from(below(rng, bound)?).ok()
}

/// An index chosen with probability proportional to its weight. `None` when
/// the weights sum to zero.
pub fn weighted_index(rng: &mut impl Rng, weights: &[u32]) -> Option<usize> {
    let total = weights.iter().map(|&weight| u64::from(weight)).sum();
    let mut target = below(rng, total)?;
    for (position, &weight) in weights.iter().enumerate() {
        let weight = u64::from(weight);
        if target < weight {
            return Some(position);
        }
        target -= weight;
    }
    None
}

#[cfg(test)]
mod tests {
    use super::*;
    use rand_chacha::ChaCha8Rng;
    use rand_core::SeedableRng;

    fn stream() -> ChaCha8Rng {
        ChaCha8Rng::seed_from_u64(42)
    }

    /// Replays a fixed list of raw values, to test edge cases exactly.
    struct Script(Vec<u64>);

    impl rand_core::TryRng for Script {
        type Error = core::convert::Infallible;

        fn try_next_u32(&mut self) -> Result<u32, Self::Error> {
            Ok(u32::try_from(self.0.remove(0) >> 32).unwrap())
        }

        fn try_next_u64(&mut self) -> Result<u64, Self::Error> {
            Ok(self.0.remove(0))
        }

        fn try_fill_bytes(&mut self, _: &mut [u8]) -> Result<(), Self::Error> {
            unimplemented!()
        }
    }

    #[test]
    fn unit_draws_stay_in_the_half_open_interval() {
        assert!((unit(&mut Script(vec![0])) - UNIT_STEP).abs() < f64::EPSILON);
        assert!((unit(&mut Script(vec![u64::MAX])) - 1.0).abs() < f64::EPSILON);
        let mut rng = stream();
        for _ in 0..10_000 {
            let value = unit(&mut rng);
            assert!(value > 0.0 && value <= 1.0);
        }
    }

    #[test]
    fn unit_draws_use_the_top_53_bits() {
        let half = unit(&mut Script(vec![1 << 63]));
        assert!((half - (0.5 + UNIT_STEP)).abs() < f64::EPSILON);
    }

    #[test]
    fn normal_draws_have_the_requested_mean_and_spread() {
        let mut rng = stream();
        let draws: Vec<f64> = (0..20_000).map(|_| normal(&mut rng, 60.0, 8.0)).collect();
        let mean = draws.iter().sum::<f64>() / 20_000.0;
        let variance = draws.iter().map(|d| (d - mean).powi(2)).sum::<f64>() / 20_000.0;
        assert!((mean - 60.0).abs() < 0.2, "mean {mean}");
        assert!(
            (variance.sqrt() - 8.0).abs() < 0.2,
            "std dev {}",
            variance.sqrt()
        );
    }

    #[test]
    fn a_zero_spread_always_gives_the_mean() {
        let mut rng = stream();
        for _ in 0..100 {
            assert!((normal(&mut rng, 55.0, 0.0) - 55.0).abs() < f64::EPSILON);
        }
    }

    #[test]
    fn normal_draws_follow_box_muller() {
        // u1 = 1 makes the radius 0; u1 = e^-0.5 makes it exactly 1, and an
        // angle of 0 makes the cosine 1.
        let one = u64::MAX;
        assert!((normal(&mut Script(vec![one, 0]), 10.0, 3.0) - 10.0).abs() < 1e-12);
        let mut rng = Script(vec![1 << 63, one]);
        let expected = 10.0 + 3.0 * libm::sqrt(-2.0 * libm::log(0.5 + UNIT_STEP));
        assert!((normal(&mut rng, 10.0, 3.0) - expected).abs() < 1e-12);
    }

    /// Pins the bits of the normal draws. This runs on Linux, Windows and
    /// macOS in CI; a failure on one of them means floats differ between
    /// platforms, which would break GEN-003.
    #[test]
    fn normal_draws_are_bit_identical_everywhere() {
        let mut rng = stream();
        let bits: Vec<u64> = (0..4)
            .map(|_| normal(&mut rng, 50.0, 10.0).to_bits())
            .collect();
        assert_eq!(bits, PINNED_NORMAL_BITS);
    }

    /// 58.327…, 40.919…, 59.269…, 55.095…
    const PINNED_NORMAL_BITS: [u64; 4] = [
        0x404d_29df_1eba_ca3a,
        0x4044_75b1_4cff_14e2,
        0x404d_a28d_b1eb_0046,
        0x404b_8c47_8915_52f4,
    ];

    #[test]
    fn below_covers_its_range_evenly() {
        let mut rng = stream();
        let mut counts = [0_u32; 5];
        for _ in 0..50_000 {
            counts[usize::try_from(below(&mut rng, 5).unwrap()).unwrap()] += 1;
        }
        for count in counts {
            assert!((9_500..10_500).contains(&count), "{counts:?}");
        }
    }

    #[test]
    fn below_rejects_values_that_would_bias_it() {
        // 2^64 mod 3 is 1, so 0 is rejected and the next value is used.
        assert_eq!(below(&mut Script(vec![0, 7]), 3), Some(1));
        assert_eq!(below(&mut Script(vec![1]), 3), Some(1));
    }

    #[test]
    fn below_gives_up_redrawing_eventually() {
        // Every value is under the threshold of 3 only if it is 0.
        let mut zeros = Script(vec![0; 64]);
        assert_eq!(below(&mut zeros, 3), Some(0));
        assert_eq!(zeros.0, Vec::<u64>::new());
    }

    #[test]
    fn below_zero_has_no_value() {
        assert_eq!(below(&mut stream(), 0), None);
    }

    #[test]
    fn below_one_is_always_zero() {
        assert_eq!(below(&mut Script(vec![u64::MAX]), 1), Some(0));
    }

    #[test]
    fn index_picks_within_the_collection() {
        assert_eq!(index(&mut Script(vec![7]), 3), Some(1));
        assert_eq!(index(&mut stream(), 0), None);
    }

    #[test]
    fn weighted_index_follows_the_weights() {
        let weights = [1, 0, 3];
        assert_eq!(weighted_index(&mut Script(vec![0]), &weights), Some(0));
        assert_eq!(weighted_index(&mut Script(vec![1]), &weights), Some(2));
        assert_eq!(weighted_index(&mut Script(vec![3]), &weights), Some(2));
        let mut rng = stream();
        let mut counts = [0_u32; 3];
        for _ in 0..40_000 {
            counts[weighted_index(&mut rng, &weights).unwrap()] += 1;
        }
        assert_eq!(counts[1], 0);
        assert!((9_500..10_500).contains(&counts[0]), "{counts:?}");
        assert!((29_500..30_500).contains(&counts[2]), "{counts:?}");
    }

    #[test]
    fn round_clamped_rounds_ties_away_and_clamps() {
        assert_eq!(round_clamped(21.5, 17, 28), 22);
        assert_eq!(round_clamped(21.49, 17, 28), 21);
        assert_eq!(round_clamped(-2.5, -10, 10), -3);
        assert_eq!(round_clamped(3.0, 17, 28), 17);
        assert_eq!(round_clamped(99.0, 17, 28), 28);
        assert_eq!(round_clamped(f64::NAN, 17, 28), 17);
        assert_eq!(round_clamped(f64::INFINITY, 17, 28), 28);
    }

    #[test]
    fn index_excluding_skips_taken_indexes() {
        let taken = std::collections::BTreeSet::from([0, 2]);
        // Free indexes are 1, 3 and 4; raw draws 3, 4 and 5 (0, 1 and 2
        // modulo 3) map onto them.
        assert_eq!(index_excluding(&mut Script(vec![3]), 5, &taken), Some(1));
        assert_eq!(index_excluding(&mut Script(vec![4]), 5, &taken), Some(3));
        assert_eq!(index_excluding(&mut Script(vec![5]), 5, &taken), Some(4));
        let all = std::collections::BTreeSet::from([0, 1]);
        assert_eq!(index_excluding(&mut stream(), 2, &all), None);
        assert_eq!(
            index_excluding(&mut stream(), 1, &std::collections::BTreeSet::from([0, 1])),
            None
        );
    }

    #[test]
    fn index_excluding_ignores_taken_entries_out_of_range() {
        let taken = std::collections::BTreeSet::from([5]);
        let mut seen = std::collections::BTreeSet::new();
        let mut rng = stream();
        for _ in 0..100 {
            seen.insert(index_excluding(&mut rng, 3, &taken).unwrap());
        }
        assert_eq!(seen, std::collections::BTreeSet::from([0, 1, 2]));
    }

    #[test]
    fn round_clamped_handles_an_empty_range() {
        assert_eq!(round_clamped(20.0, 30, 17), 30);
        assert_eq!(round_clamped(40.0, 30, 17), 30);
        assert_eq!(round_clamped(40.0, 30, 30), 30);
    }

    #[test]
    fn index_excluding_covers_every_free_index() {
        let taken = std::collections::BTreeSet::from([1, 3]);
        let mut rng = stream();
        let mut seen = std::collections::BTreeSet::new();
        for _ in 0..200 {
            let choice = index_excluding(&mut rng, 6, &taken).unwrap();
            assert!(!taken.contains(&choice));
            seen.insert(choice);
        }
        assert_eq!(seen, std::collections::BTreeSet::from([0, 2, 4, 5]));
    }

    #[test]
    fn weighted_index_needs_a_positive_total() {
        assert_eq!(weighted_index(&mut stream(), &[0, 0]), None);
        assert_eq!(weighted_index(&mut stream(), &[]), None);
    }
}
