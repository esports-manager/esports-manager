// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! The content port (packages spec): what a loaded package gives the
//! application, and what the loader reports when a package is broken.
//!
//! Errors are data: a file, a path inside it and a typed problem. The UI and
//! the CLI render them through Fluent; the loader never produces prose. Two
//! problems carry text it didn't write: `InvalidValue`, serde's description
//! of a malformed value, and `Unreadable`, the operating system's reason.

use domain::id::ContentId;
use esports::Genre;
use esports::moba::roles::RoleSetError;
use esports::moba::world::WorldTemplate;

/// A `.ftl` file of a package's own text, copied into the save. The UI
/// loads it into its Fluent bundles.
#[derive(Debug, Clone, PartialEq, Eq, serde::Serialize, specta::Type)]
#[serde(rename_all = "camelCase")]
pub struct ContentText {
    pub locale: String,
    /// Its path inside the package, such as `locales/en/teams.ftl`.
    pub file: String,
    pub source: String,
}

/// What a package declares about itself.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Manifest {
    pub id: String,
    pub version: String,
    pub title: String,
    pub license: String,
    pub authors: Vec<String>,
    pub genre: Genre,
    /// The first one is the fallback for every other.
    pub locales: Vec<String>,
}

/// A package that passed every check.
#[derive(Debug, Clone)]
pub struct Package {
    pub manifest: Manifest,
    /// SHA-256 of the package's files; saves record it (saves spec).
    pub content_hash: [u8; 32],
    /// The world the package defines, ready for the generator.
    pub template: WorldTemplate,
    pub texts: Vec<ContentText>,
}

/// A package already loaded is its own content source, so an adapter that
/// needs its text too loads it once.
impl ContentSource for Package {
    fn load(&self) -> Result<Package, Vec<PackageError>> {
        Ok(self.clone())
    }
}

/// Where the game's content comes from.
pub trait ContentSource {
    /// Loads and checks the content.
    ///
    /// # Errors
    ///
    /// Every problem found, sorted by file.
    fn load(&self) -> Result<Package, Vec<PackageError>>;
}

/// One thing wrong with a package.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PackageError {
    /// The file, relative to the package root, with `/` separators.
    pub file: String,
    /// Where in the file: `[2].reputation`, or empty for the whole file.
    pub path: String,
    pub problem: Problem,
}

/// Which name pool of a nationality is empty.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum NameKind {
    Given,
    Family,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Problem {
    /// A file or folder of the package can't be read.
    Unreadable {
        reason: String,
    },
    /// A required file, such as `manifest.json`, is missing.
    MissingFile,
    /// A top-level folder that names no content type.
    UnknownFolder,
    /// A file that doesn't belong where it is.
    UnexpectedFile,
    /// The file isn't valid JSON.
    Syntax {
        line: usize,
        column: usize,
    },
    /// A file's top level is neither an object nor a list.
    NotAnEntity,
    /// The file isn't UTF-8 text.
    NotUtf8,
    UnknownField {
        field: String,
    },
    /// The same field appears twice in one object.
    DuplicateField {
        field: String,
    },
    MissingField {
        field: String,
    },
    InvalidValue {
        detail: String,
    },
    /// A list that must not be empty, such as the manifest's locales.
    Empty,
    /// A field whose text doesn't have the required form (a date, a colour,
    /// a tag, a country code, a version).
    InvalidFormat,
    /// A number outside its allowed range.
    OutOfRange,
    InvalidId {
        id: String,
    },
    WrongKind {
        id: ContentId,
        expected: String,
    },
    DuplicateId {
        id: ContentId,
        other_file: String,
    },
    UnresolvedReference {
        field: String,
        id: String,
    },
    /// A type the package must define exactly once.
    WrongCount {
        folder: String,
        count: usize,
    },
    UnsupportedGenre {
        genre: String,
    },
    UnknownLocale {
        locale: String,
    },
    TextSyntax {
        line: usize,
    },
    MissingText {
        message: String,
        locale: String,
    },
    InvalidMix {
        region: ContentId,
    },
    EmptyNamePool {
        nationality: ContentId,
        names: NameKind,
    },
    RoleSet(RoleSetError),
    TooManySubs {
        subs: u8,
        roles: usize,
    },
    DuplicateNickname {
        nickname: String,
        player: ContentId,
        other: ContentId,
    },
    NicknamePoolTooSmall {
        distinct: usize,
        needed: usize,
    },
    IncompletableRoster {
        team: ContentId,
        missing_roles: Vec<ContentId>,
    },
}

impl PackageError {
    #[must_use]
    pub fn new(file: impl Into<String>, path: impl Into<String>, problem: Problem) -> Self {
        Self {
            file: file.into(),
            path: path.into(),
            problem,
        }
    }
}
