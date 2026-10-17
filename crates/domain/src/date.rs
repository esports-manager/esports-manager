// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! In-game calendar dates (ADR 0003: no wall-clock in the domain).
//!
//! Dates are proleptic Gregorian, with no time zone. The day-number
//! conversions are Howard Hinnant's `days_from_civil` and `civil_from_days`.

use std::fmt;
use std::str::FromStr;

/// A calendar date in the game world. Ordering is chronological.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct GameDate {
    year: u16,
    month: u8,
    day: u8,
}

/// A year, month and day that don't form a supported date.
#[derive(Debug, PartialEq, Eq, thiserror::Error)]
pub enum DateError {
    #[error("`{0}` is not a date written as YYYY-MM-DD")]
    Format(String),
    #[error("{year:04}-{month:02}-{day:02} is not a date between 0001-01-01 and 9999-12-31")]
    OutOfRange { year: u32, month: u32, day: u32 },
}

impl GameDate {
    pub const MIN: Self = Self {
        year: 1,
        month: 1,
        day: 1,
    };
    pub const MAX: Self = Self {
        year: 9999,
        month: 12,
        day: 31,
    };

    /// # Errors
    ///
    /// When the year is outside 1–9999 or the month and day don't exist.
    pub fn new(year: u32, month: u32, day: u32) -> Result<Self, DateError> {
        let error = DateError::OutOfRange { year, month, day };
        let (Ok(y), Ok(m), Ok(d)) = (u16::try_from(year), u8::try_from(month), u8::try_from(day))
        else {
            return Err(error);
        };
        let valid =
            (1..=9999).contains(&y) && (1..=12).contains(&m) && d >= 1 && d <= days_in_month(y, m);
        if valid {
            Ok(Self {
                year: y,
                month: m,
                day: d,
            })
        } else {
            Err(error)
        }
    }

    #[must_use]
    pub const fn year(self) -> u16 {
        self.year
    }

    #[must_use]
    pub const fn month(self) -> u8 {
        self.month
    }

    #[must_use]
    pub const fn day(self) -> u8 {
        self.day
    }

    /// Days since 1970-01-01 (negative before it).
    #[must_use]
    pub fn day_number(self) -> i64 {
        let month = i64::from(self.month);
        let year = i64::from(self.year) - i64::from(month <= 2);
        let era = year.div_euclid(400);
        let year_of_era = year - era * 400;
        let day_of_year = (153 * ((month + 9) % 12) + 2) / 5 + i64::from(self.day) - 1;
        let day_of_era = year_of_era * 365 + year_of_era / 4 - year_of_era / 100 + day_of_year;
        era * 146_097 + day_of_era - 719_468
    }

    /// The date `day_number` days after 1970-01-01, if it is in range.
    #[must_use]
    pub fn from_day_number(day_number: i64) -> Option<Self> {
        let shifted = day_number.checked_add(719_468)?;
        let era = shifted.div_euclid(146_097);
        let day_of_era = shifted - era * 146_097;
        let year_of_era =
            (day_of_era - day_of_era / 1460 + day_of_era / 36_524 - day_of_era / 146_096) / 365;
        let day_of_year = day_of_era - (365 * year_of_era + year_of_era / 4 - year_of_era / 100);
        let shifted_month = (5 * day_of_year + 2) / 153;
        let day = day_of_year - (153 * shifted_month + 2) / 5 + 1;
        let month = if shifted_month < 10 {
            shifted_month + 3
        } else {
            shifted_month - 9
        };
        let year = year_of_era + era * 400 + i64::from(month <= 2);
        let (year, month, day) = (
            u32::try_from(year).ok()?,
            u32::try_from(month).ok()?,
            u32::try_from(day).ok()?,
        );
        Self::new(year, month, day).ok()
    }

    /// The date `days` later (earlier when negative), if it is in range.
    #[must_use]
    pub fn add_days(self, days: i64) -> Option<Self> {
        Self::from_day_number(self.day_number().checked_add(days)?)
    }

    /// The same day `years` years earlier, or 28 February when that year has
    /// no 29 February. `None` before year 1.
    #[must_use]
    pub fn years_before(self, years: u16) -> Option<Self> {
        let year = self.year.checked_sub(years).filter(|&year| year >= 1)?;
        let day = self.day.min(days_in_month(year, self.month));
        Some(Self {
            year,
            month: self.month,
            day,
        })
    }

    /// Completed years from `self` (a birth date) to `on`, or `None` when `on`
    /// is before `self`. Someone born on 29 February turns a year older on
    /// 1 March in common years.
    #[must_use]
    pub fn age_on(self, on: Self) -> Option<u16> {
        if on < self {
            return None;
        }
        let had_birthday = (on.month, on.day) >= (self.month, self.day);
        Some(on.year - self.year - u16::from(!had_birthday))
    }
}

const fn is_leap_year(year: u16) -> bool {
    (year.is_multiple_of(4) && !year.is_multiple_of(100)) || year.is_multiple_of(400)
}

const fn days_in_month(year: u16, month: u8) -> u8 {
    match month {
        2 if is_leap_year(year) => 29,
        2 => 28,
        4 | 6 | 9 | 11 => 30,
        _ => 31,
    }
}

impl fmt::Display for GameDate {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{:04}-{:02}-{:02}", self.year, self.month, self.day)
    }
}

impl FromStr for GameDate {
    type Err = DateError;

    /// Parses `YYYY-MM-DD`, the form packages and saves use.
    fn from_str(text: &str) -> Result<Self, Self::Err> {
        let format = || DateError::Format(text.to_owned());
        let bytes = text.as_bytes();
        let shaped = bytes.len() == 10
            && bytes[4] == b'-'
            && bytes[7] == b'-'
            && bytes
                .iter()
                .enumerate()
                .all(|(index, byte)| index == 4 || index == 7 || byte.is_ascii_digit());
        if !shaped {
            return Err(format());
        }
        let number =
            |range: std::ops::Range<usize>| text[range].parse::<u32>().map_err(|_| format());
        Self::new(number(0..4)?, number(5..7)?, number(8..10)?)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn date(text: &str) -> GameDate {
        text.parse().unwrap()
    }

    #[test]
    fn a_date_keeps_its_parts() {
        let start = GameDate::new(2027, 3, 14).unwrap();
        assert_eq!((start.year(), start.month(), start.day()), (2027, 3, 14));
        assert_eq!(start.to_string(), "2027-03-14");
    }

    #[test]
    fn days_that_do_not_exist_are_rejected() {
        for (year, month, day) in [
            (2027, 2, 29),
            (2100, 2, 29),
            (2027, 4, 31),
            (2027, 13, 1),
            (2027, 0, 1),
            (2027, 1, 0),
            (2027, 1, 32),
            (0, 1, 1),
            (10_000, 1, 1),
            (70_000, 1, 1),
            (2027, 300, 1),
            (2027, 1, 300),
        ] {
            assert_eq!(
                GameDate::new(year, month, day),
                Err(DateError::OutOfRange { year, month, day }),
                "{year}-{month}-{day}"
            );
        }
    }

    #[test]
    fn leap_days_exist_in_leap_years() {
        assert!(GameDate::new(2028, 2, 29).is_ok());
        assert!(GameDate::new(2000, 2, 29).is_ok());
    }

    #[test]
    fn month_lengths_follow_the_calendar() {
        for (month, days) in [
            (1, 31),
            (2, 28),
            (3, 31),
            (4, 30),
            (5, 31),
            (6, 30),
            (7, 31),
            (8, 31),
            (9, 30),
            (10, 31),
            (11, 30),
            (12, 31),
        ] {
            assert!(GameDate::new(2027, month, days).is_ok(), "{month}");
            assert!(GameDate::new(2027, month, days + 1).is_err(), "{month}");
        }
    }

    #[test]
    fn parses_and_formats_iso_dates() {
        assert_eq!(date("2027-01-01"), GameDate::new(2027, 1, 1).unwrap());
        assert_eq!(date("0001-01-01"), GameDate::MIN);
        assert_eq!(date("9999-12-31"), GameDate::MAX);
        assert_eq!(GameDate::MIN.to_string(), "0001-01-01");
    }

    #[test]
    fn malformed_text_is_rejected() {
        for text in [
            "2027-1-01",
            "2027/01/01",
            "27-01-01",
            "2027-01-011",
            "2027-0a-01",
            "",
            "+027-01-01",
        ] {
            assert_eq!(
                text.parse::<GameDate>(),
                Err(DateError::Format(text.to_owned())),
                "{text}"
            );
        }
        assert!("2027-02-30".parse::<GameDate>().is_err());
    }

    #[test]
    fn day_numbers_count_from_1970() {
        assert_eq!(date("1970-01-01").day_number(), 0);
        assert_eq!(date("1970-01-02").day_number(), 1);
        assert_eq!(date("1969-12-31").day_number(), -1);
        assert_eq!(date("2000-03-01").day_number(), 11_017);
        assert_eq!(date("2027-01-01").day_number(), 20_819);
        assert_eq!(GameDate::MIN.day_number(), -719_162);
        assert_eq!(GameDate::MAX.day_number(), 2_932_896);
    }

    #[test]
    fn day_numbers_round_trip_across_the_range() {
        let mut day = GameDate::MIN.day_number();
        let mut previous = None;
        while day <= GameDate::MAX.day_number() {
            let current = GameDate::from_day_number(day).unwrap();
            assert_eq!(current.day_number(), day);
            if let Some(previous) = previous {
                assert!(previous < current);
            }
            previous = Some(current);
            day += 1;
        }
    }

    #[test]
    fn day_numbers_outside_the_range_have_no_date() {
        assert_eq!(
            GameDate::from_day_number(GameDate::MIN.day_number() - 1),
            None
        );
        assert_eq!(
            GameDate::from_day_number(GameDate::MAX.day_number() + 1),
            None
        );
        assert_eq!(GameDate::from_day_number(i64::MAX), None);
        assert_eq!(GameDate::from_day_number(i64::MIN), None);
    }

    #[test]
    fn adding_days_crosses_months_and_years() {
        assert_eq!(date("2027-12-31").add_days(1), Some(date("2028-01-01")));
        assert_eq!(date("2028-02-28").add_days(1), Some(date("2028-02-29")));
        assert_eq!(date("2027-03-01").add_days(-1), Some(date("2027-02-28")));
        assert_eq!(GameDate::MAX.add_days(1), None);
        assert_eq!(GameDate::MIN.add_days(i64::MIN), None);
    }

    #[test]
    fn age_counts_completed_years_on_the_game_date() {
        // spec: ROST-004
        // Given
        let today = date("2027-01-01");
        let birth = date("2000-01-02");
        // When
        let age = birth.age_on(today);
        // Then
        assert_eq!(age, Some(26));
    }

    #[test]
    fn age_increases_on_the_birthday() {
        let birth = date("2000-01-02");
        assert_eq!(birth.age_on(date("2027-01-02")), Some(27));
        assert_eq!(birth.age_on(date("2000-01-02")), Some(0));
        assert_eq!(birth.age_on(date("2001-01-01")), Some(0));
    }

    #[test]
    fn leap_day_birthdays_count_from_1_march_in_common_years() {
        let birth = date("2008-02-29");
        assert_eq!(birth.age_on(date("2027-02-28")), Some(18));
        assert_eq!(birth.age_on(date("2027-03-01")), Some(19));
        assert_eq!(birth.age_on(date("2028-02-29")), Some(20));
    }

    #[test]
    fn years_before_keeps_the_day_where_it_exists() {
        assert_eq!(
            date("2027-01-01").years_before(29),
            Some(date("1998-01-01"))
        );
        assert_eq!(date("2028-02-29").years_before(1), Some(date("2027-02-28")));
        assert_eq!(date("2028-02-29").years_before(4), Some(date("2024-02-29")));
        assert_eq!(date("2027-03-14").years_before(0), Some(date("2027-03-14")));
        assert_eq!(date("2027-03-14").years_before(2027), None);
        assert_eq!(
            date("2027-03-14").years_before(2026),
            Some(date("0001-03-14"))
        );
    }

    #[test]
    fn there_is_no_age_before_birth() {
        assert_eq!(date("2000-01-02").age_on(date("2000-01-01")), None);
    }
}
