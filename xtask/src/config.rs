// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! `quality.toml`: the enforced numbers and lists behind the ADRs.

use std::collections::BTreeMap;
use std::path::Path;

use anyhow::{Context, Result};
use serde::Deserialize;

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Quality {
    pub coverage: BTreeMap<String, u32>,
    pub architecture: Architecture,
    pub vocabulary: Vocabulary,
    pub packages: Packages,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Architecture {
    pub allowed: BTreeMap<String, Vec<String>>,
    pub banned: BTreeMap<String, Vec<String>>,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Vocabulary {
    #[serde(rename = "crate")]
    pub crate_name: String,
    pub denied: Vec<String>,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Packages {
    /// Modules converting package types to domain types, where rest
    /// patterns are banned.
    pub conversion: Vec<String>,
}

impl Quality {
    pub fn load(path: &Path) -> Result<Self> {
        let text =
            std::fs::read_to_string(path).with_context(|| format!("reading {}", path.display()))?;
        Self::parse(&text).with_context(|| format!("parsing {}", path.display()))
    }

    fn parse(text: &str) -> Result<Self> {
        Ok(toml::from_str(text)?)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_every_section() {
        let quality = Quality::parse(
            r#"
            [coverage]
            domain = 90

            [architecture.allowed]
            domain = []
            app = ["domain"]

            [architecture.banned]
            domain = ["tokio"]

            [vocabulary]
            crate = "domain"
            denied = ["lane"]

            [packages]
            conversion = ["crates/packages/src/convert.rs"]
            "#,
        )
        .unwrap();

        assert_eq!(quality.coverage["domain"], 90);
        assert_eq!(quality.architecture.allowed["app"], ["domain"]);
        assert_eq!(quality.architecture.banned["domain"], ["tokio"]);
        assert_eq!(quality.vocabulary.crate_name, "domain");
        assert_eq!(quality.vocabulary.denied, ["lane"]);
        assert_eq!(
            quality.packages.conversion,
            ["crates/packages/src/convert.rs"]
        );
    }

    #[test]
    fn rejects_unknown_keys() {
        let result = Quality::parse(
            r#"
            [coverage]
            [architecture.allowed]
            [architecture.banned]
            [vocabulary]
            crate = "domain"
            denied = []
            surprise = true
            [packages]
            conversion = []
            "#,
        );
        assert!(result.is_err());
    }

    #[test]
    fn the_repository_config_parses() {
        let path = Path::new(env!("CARGO_MANIFEST_DIR")).join("../quality.toml");
        assert!(Quality::load(&path).is_ok());
    }
}
