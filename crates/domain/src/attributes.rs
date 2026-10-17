// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! The attributes every genre shares (attributes spec).
//!
//! Genre modules add their own skills. These are the traits, which describe
//! personality, and the hidden attributes, which are only ever estimated.

use crate::rating::Rating;

/// Personality traits: slow to change, shown to the user.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum CoreTrait {
    Teamwork,
    Aggression,
    Composure,
    WorkEthic,
}

impl CoreTrait {
    pub const ALL: [Self; 4] = [
        Self::Teamwork,
        Self::Aggression,
        Self::Composure,
        Self::WorkEthic,
    ];
}

/// Attributes the user never sees as numbers.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum HiddenAttribute {
    Consistency,
    Potential,
}

impl HiddenAttribute {
    pub const ALL: [Self; 2] = [Self::Consistency, Self::Potential];
}

/// A person's traits and hidden attributes.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct CoreAttributes {
    pub teamwork: Rating,
    pub aggression: Rating,
    pub composure: Rating,
    pub work_ethic: Rating,
    pub consistency: Rating,
    pub potential: Rating,
}

impl CoreAttributes {
    /// Every attribute at the same rating, mostly useful as a starting point.
    #[must_use]
    pub const fn uniform(rating: Rating) -> Self {
        Self {
            teamwork: rating,
            aggression: rating,
            composure: rating,
            work_ethic: rating,
            consistency: rating,
            potential: rating,
        }
    }

    #[must_use]
    pub const fn get_trait(&self, which: CoreTrait) -> Rating {
        match which {
            CoreTrait::Teamwork => self.teamwork,
            CoreTrait::Aggression => self.aggression,
            CoreTrait::Composure => self.composure,
            CoreTrait::WorkEthic => self.work_ethic,
        }
    }

    #[must_use]
    pub const fn get_hidden(&self, which: HiddenAttribute) -> Rating {
        match which {
            HiddenAttribute::Consistency => self.consistency,
            HiddenAttribute::Potential => self.potential,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn rating(points: u32) -> Rating {
        Rating::from_points(points).unwrap()
    }

    fn distinct() -> CoreAttributes {
        CoreAttributes {
            teamwork: rating(11),
            aggression: rating(12),
            composure: rating(13),
            work_ethic: rating(14),
            consistency: rating(15),
            potential: rating(16),
        }
    }

    #[test]
    fn traits_read_their_own_field() {
        let attributes = distinct();
        let values: Vec<u8> = CoreTrait::ALL
            .iter()
            .map(|&t| attributes.get_trait(t).display())
            .collect();
        assert_eq!(values, [11, 12, 13, 14]);
    }

    #[test]
    fn hidden_attributes_read_their_own_field() {
        let attributes = distinct();
        let values: Vec<u8> = HiddenAttribute::ALL
            .iter()
            .map(|&h| attributes.get_hidden(h).display())
            .collect();
        assert_eq!(values, [15, 16]);
    }

    #[test]
    fn uniform_sets_every_attribute() {
        let attributes = CoreAttributes::uniform(rating(40));
        assert!(
            CoreTrait::ALL
                .iter()
                .all(|&t| attributes.get_trait(t) == rating(40))
        );
        assert!(
            HiddenAttribute::ALL
                .iter()
                .all(|&h| attributes.get_hidden(h) == rating(40))
        );
    }
}
