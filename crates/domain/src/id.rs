// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Stable string ids for content, such as `team:azure_tigers` (ADR 0005).
//!
//! An id is a kind and a slug separated by `:`. Packages write slugs with
//! `a-z`, `0-9` and `_` only. Ids the generator creates add `.<n>` to a slug
//! (`player:azure_tigers.3`), so they can never collide with a package id.

use std::fmt;

/// A content id. Ordering is byte order of its text, which is what every
/// "ties go to the lower id" rule means.
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct ContentId {
    text: String,
    colon: usize,
}

/// Why a text isn't a valid id.
#[derive(Debug, Clone, Copy, PartialEq, Eq, thiserror::Error)]
pub enum IdError {
    #[error("an id needs a `:` between its kind and its slug")]
    MissingColon,
    #[error("the kind before `:` is empty or has characters other than a-z and _")]
    InvalidKind,
    #[error("the slug after `:` is empty or has characters other than a-z, 0-9 and _")]
    InvalidSlug,
}

impl ContentId {
    /// Parses an id as a package writes it, with no generated suffix.
    ///
    /// # Errors
    ///
    /// When the text isn't `<kind>:<slug>` with a valid kind and slug.
    pub fn parse(text: &str) -> Result<Self, IdError> {
        let (kind, slug) = split(text)?;
        if !is_slug(slug) {
            return Err(IdError::InvalidSlug);
        }
        Ok(Self::from_parts(kind, slug))
    }

    /// Parses an id read back from a save, which may be a generated one.
    ///
    /// # Errors
    ///
    /// When the text is neither a package id nor a generated id.
    pub fn parse_stored(text: &str) -> Result<Self, IdError> {
        let (kind, slug) = split(text)?;
        let valid = match slug.split_once('.') {
            None => is_slug(slug),
            Some((base, number)) => is_slug(base) && is_number(number),
        };
        if !valid {
            return Err(IdError::InvalidSlug);
        }
        Ok(Self::from_parts(kind, slug))
    }

    /// The id of the `number`th thing of `kind` the generator creates for
    /// `owner`: `generated("player", team:azure_tigers, 3)` is
    /// `player:azure_tigers.3`.
    ///
    /// # Errors
    ///
    /// When `kind` isn't a valid kind, or `owner` is itself generated.
    pub fn generated(kind: &str, owner: &Self, number: u32) -> Result<Self, IdError> {
        if !is_kind(kind) {
            return Err(IdError::InvalidKind);
        }
        // `player:a.1.2` would not parse back, so a generated id can't own one.
        if owner.is_generated() {
            return Err(IdError::InvalidSlug);
        }
        Ok(Self::from_parts(
            kind,
            &format!("{}.{number}", owner.slug()),
        ))
    }

    /// Whether `text` is a slug as packages write them: `a-z`, `0-9` and `_`.
    #[must_use]
    pub fn is_slug(text: &str) -> bool {
        is_slug(text)
    }

    fn from_parts(kind: &str, slug: &str) -> Self {
        Self {
            text: format!("{kind}:{slug}"),
            colon: kind.len(),
        }
    }

    #[must_use]
    pub fn kind(&self) -> &str {
        &self.text[..self.colon]
    }

    #[must_use]
    pub fn slug(&self) -> &str {
        &self.text[self.colon + 1..]
    }

    /// Whether the generator created this id.
    #[must_use]
    pub fn is_generated(&self) -> bool {
        self.slug().contains('.')
    }

    #[must_use]
    pub fn as_str(&self) -> &str {
        &self.text
    }

    /// The Fluent message holding this content's translatable name:
    /// `team:azure_tigers` → `team-azure_tigers` (packages spec). Only
    /// package content has a name in package text; for a generated id the
    /// result names no message.
    #[must_use]
    pub fn message_id(&self) -> String {
        format!("{}-{}", self.kind(), self.slug())
    }
}

impl fmt::Display for ContentId {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.text)
    }
}

fn split(text: &str) -> Result<(&str, &str), IdError> {
    let (kind, slug) = text.split_once(':').ok_or(IdError::MissingColon)?;
    if !is_kind(kind) {
        return Err(IdError::InvalidKind);
    }
    Ok((kind, slug))
}

fn is_kind(text: &str) -> bool {
    !text.is_empty() && text.bytes().all(|b| b.is_ascii_lowercase() || b == b'_')
}

fn is_slug(text: &str) -> bool {
    !text.is_empty()
        && text
            .bytes()
            .all(|b| b.is_ascii_lowercase() || b.is_ascii_digit() || b == b'_')
}

fn is_number(text: &str) -> bool {
    !text.is_empty() && text.bytes().all(|b| b.is_ascii_digit())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn id(text: &str) -> ContentId {
        ContentId::parse(text).unwrap()
    }

    #[test]
    fn slugs_are_lowercase_letters_digits_and_underscores() {
        assert!(ContentId::is_slug("azure_tigers_2"));
        for text in ["", "Azure", "azure-tigers", "a.b", "a:b"] {
            assert!(!ContentId::is_slug(text), "{text}");
        }
    }

    #[test]
    fn a_package_id_has_a_kind_and_a_slug() {
        let team = id("team:azure_tigers");
        assert_eq!(team.kind(), "team");
        assert_eq!(team.slug(), "azure_tigers");
        assert_eq!(team.as_str(), "team:azure_tigers");
        assert_eq!(team.to_string(), "team:azure_tigers");
        assert!(!team.is_generated());
    }

    #[test]
    fn slugs_may_hold_digits_and_underscores() {
        assert_eq!(id("team:pulse_7").slug(), "pulse_7");
    }

    #[test]
    fn kinds_may_hold_underscores() {
        assert_eq!(id("name_pool:kr").kind(), "name_pool");
    }

    #[test]
    fn malformed_ids_are_rejected() {
        let cases = [
            ("team", IdError::MissingColon),
            (":azure", IdError::InvalidKind),
            ("Team:azure", IdError::InvalidKind),
            ("team2:azure", IdError::InvalidKind),
            ("team:", IdError::InvalidSlug),
            ("team:Azure", IdError::InvalidSlug),
            ("team:azure-tigers", IdError::InvalidSlug),
            ("team:azure:tigers", IdError::InvalidSlug),
        ];
        for (text, error) in cases {
            assert_eq!(ContentId::parse(text), Err(error), "{text}");
        }
    }

    #[test]
    fn packages_cannot_write_generated_ids() {
        assert_eq!(
            ContentId::parse("player:azure_tigers.3"),
            Err(IdError::InvalidSlug)
        );
    }

    #[test]
    fn generated_ids_extend_their_owner_slug() {
        let player = ContentId::generated("player", &id("team:azure_tigers"), 3).unwrap();
        assert_eq!(player.as_str(), "player:azure_tigers.3");
        assert_eq!(player.kind(), "player");
        assert!(player.is_generated());
    }

    #[test]
    fn generated_ids_cant_be_owned_by_generated_ids() {
        let player = ContentId::generated("player", &id("team:a"), 1).unwrap();
        assert_eq!(
            ContentId::generated("player", &player, 2),
            Err(IdError::InvalidSlug)
        );
    }

    #[test]
    fn generated_ids_need_a_valid_kind() {
        assert_eq!(
            ContentId::generated("Player", &id("team:a"), 1),
            Err(IdError::InvalidKind)
        );
    }

    #[test]
    fn stored_ids_may_be_package_or_generated_ids() {
        assert_eq!(
            ContentId::parse_stored("team:azure_tigers"),
            Ok(id("team:azure_tigers"))
        );
        let generated = ContentId::parse_stored("player:azure_tigers.12").unwrap();
        assert_eq!(generated.slug(), "azure_tigers.12");
        assert!(generated.is_generated());
    }

    #[test]
    fn malformed_stored_ids_are_rejected() {
        for text in [
            "player:azure_tigers.",
            "player:.3",
            "player:azure_tigers.x",
            "player:a.1.2",
            "player:A.1",
            "player",
            "Player:a.1",
        ] {
            assert!(ContentId::parse_stored(text).is_err(), "{text}");
        }
    }

    #[test]
    fn message_ids_replace_the_colon_with_a_dash() {
        assert_eq!(id("team:azure_tigers").message_id(), "team-azure_tigers");
        assert_eq!(id("name_pool:kr").message_id(), "name_pool-kr");
    }

    #[test]
    fn ids_order_by_their_text() {
        assert!(id("player:a") < id("player:b"));
        assert!(id("player:b") < id("team:a"));
    }
}
