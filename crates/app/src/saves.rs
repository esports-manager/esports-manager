// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! The save port (saves spec): what the application needs from storage. The
//! `db` crate implements it with one SQLite file per save.

use domain::date::GameDate;
use domain::id::ContentId;
use domain::rng::WorldSeed;
use domain::world::{Competition, Nationality, Region, Team};
use esports::Genre;
use esports::moba::roles::RoleSet;
use esports::moba::world::{Player, World};

use crate::content::ContentText;

/// Real time, in whole seconds since the Unix epoch. Only adapters read the
/// clock; the domain never sees this (ADR 0003).
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct Timestamp(pub i64);

/// A package a save was built from.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PackageRecord {
    pub id: String,
    pub version: String,
    pub content_hash: [u8; 32],
}

/// What every save records about itself (`save_meta`).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SaveMeta {
    /// The name the user typed.
    pub name: String,
    pub manager_name: String,
    pub team: ContentId,
    pub genre: Genre,
    pub seed: WorldSeed,
    /// The game version that created the save.
    pub game_version: String,
    pub game_date: GameDate,
    pub created_at: Timestamp,
    pub last_played_at: Timestamp,
    pub packages: Vec<PackageRecord>,
}

/// Everything a new save holds. The store takes it whole, since New Game
/// has no use for it once it is written.
#[derive(Debug)]
pub struct NewSave {
    pub meta: SaveMeta,
    pub world: World,
    pub texts: Vec<ContentText>,
}

/// Why a save file can't be used.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Damage {
    NotASave,
    /// Made by a newer version of the game.
    NewerVersion,
}

/// One file in the saves folder.
#[derive(Debug, PartialEq, Eq)]
pub struct SaveListing {
    /// The file name, such as `ana-s-tigers.esmsave`. It identifies the save.
    pub file: String,
    pub save: Result<SaveMeta, Damage>,
    /// Whether a process holds the save open. Its metadata is still listed;
    /// only opening it is refused.
    pub in_use: bool,
}

#[derive(Debug, Clone, PartialEq, Eq, thiserror::Error)]
pub enum SaveError {
    #[error("a save named `{0}` already exists")]
    NameTaken(String),
    #[error("there is no save `{0}`")]
    NotFound(String),
    #[error("the save is not a save file")]
    NotASave,
    #[error("the save was made by a newer version of the game")]
    NewerVersion,
    #[error("the save is open in another process")]
    InUse,
    #[error("storage failed: {0}")]
    Storage(String),
}

impl From<Damage> for SaveError {
    fn from(damage: Damage) -> Self {
        match damage {
            Damage::NotASave => Self::NotASave,
            Damage::NewerVersion => Self::NewerVersion,
        }
    }
}

/// Where saves live.
pub trait SaveStore {
    type Save: OpenSave;

    /// Writes a new save and returns its file name.
    ///
    /// # Errors
    ///
    /// When the name is taken (ignoring case) or storage fails. A failed
    /// creation leaves nothing behind.
    fn create(&self, save: NewSave) -> Result<String, SaveError>;

    /// Every save in the folder, newest first; damaged files included.
    ///
    /// # Errors
    ///
    /// When the folder itself can't be read.
    fn list(&self) -> Result<Vec<SaveListing>, SaveError>;

    /// Opens a save for this process alone and records `now` as its last
    /// played time.
    ///
    /// # Errors
    ///
    /// When it doesn't exist, is damaged, newer than the game, or open
    /// elsewhere.
    fn open(&self, file: &str, now: Timestamp) -> Result<Self::Save, SaveError>;
}

/// A save this process holds open.
pub trait OpenSave {
    fn meta(&self) -> &SaveMeta;

    /// # Errors
    ///
    /// When storage fails.
    fn team(&mut self, id: &ContentId) -> Result<Option<Team>, SaveError>;

    /// The players of a team, in the order the world was generated.
    ///
    /// # Errors
    ///
    /// When storage fails.
    fn players_of(&mut self, team: &ContentId) -> Result<Vec<Player>, SaveError>;

    /// # Errors
    ///
    /// When storage fails.
    fn player(&mut self, id: &ContentId) -> Result<Option<Player>, SaveError>;

    /// # Errors
    ///
    /// When storage fails.
    fn roles(&mut self) -> Result<RoleSet, SaveError>;

    /// # Errors
    ///
    /// When storage fails.
    fn regions(&mut self) -> Result<Vec<Region>, SaveError>;

    /// # Errors
    ///
    /// When storage fails.
    fn nationalities(&mut self) -> Result<Vec<Nationality>, SaveError>;

    /// # Errors
    ///
    /// When storage fails.
    fn competitions(&mut self) -> Result<Vec<Competition>, SaveError>;

    /// # Errors
    ///
    /// When storage fails.
    fn texts(&mut self) -> Result<Vec<ContentText>, SaveError>;
}
