// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Ratings on the 1–99 scale, stored in whole hundredths (attributes spec).

use std::fmt;

/// An attribute or overall, from 1.00 to 99.00, held as an integer number of
/// hundredths so no float ever reaches a save.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct Rating(u16);

/// A rating outside 1.00–99.00.
#[derive(Debug, Clone, Copy, PartialEq, Eq, thiserror::Error)]
#[error("{hundredths} hundredths is outside the 1.00–99.00 rating scale")]
pub struct RatingOutOfRange {
    pub hundredths: u32,
}

impl Rating {
    pub const MIN: Self = Self(100);
    pub const MAX: Self = Self(9900);

    /// # Errors
    ///
    /// When the value is outside 100–9900 hundredths.
    pub fn from_hundredths(hundredths: u32) -> Result<Self, RatingOutOfRange> {
        u16::try_from(hundredths)
            .ok()
            .filter(|value| (Self::MIN.0..=Self::MAX.0).contains(value))
            .map(Self)
            .ok_or(RatingOutOfRange { hundredths })
    }

    /// A whole-number rating, as packages usually write them.
    ///
    /// # Errors
    ///
    /// When the value is outside 1–99.
    pub fn from_points(points: u32) -> Result<Self, RatingOutOfRange> {
        Self::from_hundredths(points.saturating_mul(100))
    }

    /// Rounds `points` to the nearest hundredth, ties away from zero, and
    /// clamps it to the scale. Clamping, not folding: a draw below the scale
    /// becomes 1.00. A NaN becomes 1.00 too, so the result is always defined.
    #[must_use]
    pub fn clamped(points: f64) -> Self {
        let hundredths = (points * 100.0).round();
        if hundredths.is_nan() {
            return Self::MIN;
        }
        let bounded = hundredths.clamp(f64::from(Self::MIN.0), f64::from(Self::MAX.0));
        #[expect(
            clippy::cast_possible_truncation,
            clippy::cast_sign_loss,
            reason = "rounded and clamped to 100..=9900 just above"
        )]
        let value = bounded as u16;
        Self(value)
    }

    #[must_use]
    pub const fn hundredths(self) -> u16 {
        self.0
    }

    /// The rating as a float, for draws and biases that work in points.
    #[must_use]
    pub fn points(self) -> f64 {
        f64::from(self.0) / 100.0
    }

    /// The whole number shown to the user, rounded with ties away from zero:
    /// 72.49 shows as 72 and 72.50 as 73.
    #[must_use]
    pub const fn display(self) -> u8 {
        // At most (9900 + 50) / 100 = 99, so the narrowing is exact.
        let whole = (self.0 + 50) / 100;
        whole.to_le_bytes()[0]
    }
}

impl fmt::Display for Rating {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}.{:02}", self.0 / 100, self.0 % 100)
    }
}

/// The weighted mean of ratings, rounded to the nearest hundredth with ties
/// away from zero. `None` when the weights sum to zero.
#[must_use]
pub fn weighted_mean(terms: impl IntoIterator<Item = (Rating, u32)>) -> Option<Rating> {
    let (sum, total) = terms
        .into_iter()
        .fold((0_u64, 0_u64), |(sum, total), (rating, weight)| {
            (
                sum + u64::from(weight) * u64::from(rating.0),
                total + u64::from(weight),
            )
        });
    if total == 0 {
        return None;
    }
    // floor(sum / total + 1/2), all in integers.
    let mean = (2 * sum + total) / (2 * total);
    // A mean of in-range ratings is in range; the fallback is unreachable.
    Some(Rating::from_mean(mean))
}

impl Rating {
    fn from_mean(hundredths: u64) -> Self {
        u16::try_from(hundredths).map_or(Self::MAX, |value| {
            Self(value.clamp(Self::MIN.0, Self::MAX.0))
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn rating(hundredths: u32) -> Rating {
        Rating::from_hundredths(hundredths).unwrap()
    }

    #[test]
    fn the_scale_runs_from_1_to_99() {
        assert_eq!(Rating::MIN.hundredths(), 100);
        assert_eq!(Rating::MAX.hundredths(), 9900);
        assert_eq!(rating(100), Rating::MIN);
        assert_eq!(rating(9900), Rating::MAX);
    }

    #[test]
    fn values_off_the_scale_are_rejected() {
        for hundredths in [0, 99, 9901, 70_000] {
            assert_eq!(
                Rating::from_hundredths(hundredths),
                Err(RatingOutOfRange { hundredths })
            );
        }
    }

    #[test]
    fn whole_points_convert_to_hundredths() {
        assert_eq!(Rating::from_points(1), Ok(Rating::MIN));
        assert_eq!(Rating::from_points(95), Ok(rating(9500)));
        assert_eq!(Rating::from_points(99), Ok(Rating::MAX));
        assert!(Rating::from_points(0).is_err());
        assert!(Rating::from_points(100).is_err());
        assert!(Rating::from_points(u32::MAX).is_err());
    }

    #[test]
    fn floats_round_to_the_nearest_hundredth() {
        assert_eq!(Rating::clamped(72.494), rating(7249));
        assert_eq!(Rating::clamped(72.496), rating(7250));
        assert_eq!(Rating::clamped(50.0), rating(5000));
    }

    #[test]
    fn floats_off_the_scale_are_clamped_not_folded() {
        assert_eq!(Rating::clamped(-12.0), Rating::MIN);
        assert_eq!(Rating::clamped(0.5), Rating::MIN);
        assert_eq!(Rating::clamped(99.004), Rating::MAX);
        assert_eq!(Rating::clamped(140.0), Rating::MAX);
        assert_eq!(Rating::clamped(f64::INFINITY), Rating::MAX);
        assert_eq!(Rating::clamped(f64::NEG_INFINITY), Rating::MIN);
        assert_eq!(Rating::clamped(f64::NAN), Rating::MIN);
    }

    #[test]
    fn points_are_the_hundredths_as_a_float() {
        assert!((rating(7250).points() - 72.5).abs() < f64::EPSILON);
    }

    #[test]
    fn display_rounds_ties_away_from_zero() {
        // spec: ATTR-004
        // Given
        let below_tie = rating(7249);
        let tie = rating(7250);
        // When
        let shown = (below_tie.display(), tie.display());
        // Then
        assert_eq!(shown, (72, 73));
    }

    #[test]
    fn display_covers_the_ends_of_the_scale() {
        assert_eq!(Rating::MIN.display(), 1);
        assert_eq!(rating(149).display(), 1);
        assert_eq!(rating(150).display(), 2);
        assert_eq!(Rating::MAX.display(), 99);
    }

    #[test]
    fn formats_with_two_decimals() {
        assert_eq!(rating(7405).to_string(), "74.05");
        assert_eq!(Rating::MIN.to_string(), "1.00");
    }

    #[test]
    fn the_weighted_mean_weighs_each_rating() {
        let mean = weighted_mean([(rating(9000), 20), (rating(7000), 80)]);
        assert_eq!(mean, Some(rating(7400)));
    }

    #[test]
    fn the_weighted_mean_rounds_ties_away_from_zero() {
        assert_eq!(
            weighted_mean([(rating(7000), 1), (rating(7001), 1)]),
            Some(rating(7001))
        );
        assert_eq!(
            weighted_mean([(rating(7000), 2), (rating(7001), 1)]),
            Some(rating(7000))
        );
    }

    #[test]
    fn zero_weights_are_ignored() {
        assert_eq!(
            weighted_mean([(rating(9000), 1), (rating(1000), 0)]),
            Some(rating(9000))
        );
    }

    #[test]
    fn no_weight_means_no_mean() {
        assert_eq!(weighted_mean([(rating(9000), 0)]), None);
        assert_eq!(weighted_mean([]), None);
    }

    #[test]
    fn the_mean_of_extremes_stays_on_the_scale() {
        assert_eq!(
            weighted_mean([(Rating::MAX, u32::MAX), (Rating::MAX, u32::MAX)]),
            Some(Rating::MAX)
        );
        assert_eq!(weighted_mean([(Rating::MIN, 3)]), Some(Rating::MIN));
    }

    #[test]
    fn out_of_range_means_are_pinned_to_the_scale() {
        assert_eq!(Rating::from_mean(50), Rating::MIN);
        assert_eq!(Rating::from_mean(9950), Rating::MAX);
        assert_eq!(Rating::from_mean(u64::MAX), Rating::MAX);
        assert_eq!(Rating::from_mean(4321), rating(4321));
    }
}
