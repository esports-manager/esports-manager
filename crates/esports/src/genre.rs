// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

use std::fmt;
use std::str::FromStr;

/// The esport a world is built around. A save holds exactly one (ADR 0002).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum Genre {
    Moba,
}

impl Genre {
    /// Every genre the game supports.
    pub const ALL: [Self; 1] = [Self::Moba];

    /// The stable identifier used in package manifests and saves.
    #[must_use]
    pub const fn id(self) -> &'static str {
        match self {
            Self::Moba => "moba",
        }
    }
}

impl fmt::Display for Genre {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(self.id())
    }
}

/// A genre identifier that no supported genre uses.
#[derive(Debug, PartialEq, Eq, thiserror::Error)]
#[error("unknown genre id `{id}`")]
pub struct UnknownGenre {
    pub id: String,
}

impl FromStr for Genre {
    type Err = UnknownGenre;

    fn from_str(id: &str) -> Result<Self, Self::Err> {
        Self::ALL
            .into_iter()
            .find(|genre| genre.id() == id)
            .ok_or_else(|| UnknownGenre { id: id.to_owned() })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn moba_has_a_stable_id() {
        assert_eq!(Genre::Moba.id(), "moba");
    }

    #[test]
    fn display_writes_the_id() {
        assert_eq!(Genre::Moba.to_string(), "moba");
    }

    #[test]
    fn every_genre_parses_back_from_its_id() {
        for genre in Genre::ALL {
            assert_eq!(genre.id().parse::<Genre>(), Ok(genre));
        }
    }

    #[test]
    fn unknown_ids_are_rejected() {
        assert_eq!(
            "chess".parse::<Genre>(),
            Err(UnknownGenre {
                id: "chess".to_owned()
            })
        );
    }

    #[test]
    fn ids_are_case_sensitive() {
        assert!("MOBA".parse::<Genre>().is_err());
    }
}
