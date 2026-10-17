// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

use serde::Serialize;

/// What the game reports about itself. Every adapter shows the version from
/// here, so there is one source for it.
#[derive(Debug, PartialEq, Eq, Serialize, specta::Type)]
#[serde(rename_all = "camelCase")]
pub struct About {
    pub version: String,
}

#[must_use]
pub fn about() -> About {
    About {
        version: env!("CARGO_PKG_VERSION").to_owned(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn reports_the_workspace_version() {
        assert_eq!(about().version, env!("CARGO_PKG_VERSION"));
    }

    #[test]
    fn the_version_is_not_empty() {
        assert_ne!(about().version, "");
    }
}
