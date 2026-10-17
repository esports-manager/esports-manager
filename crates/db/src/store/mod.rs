// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! One SQLite file per save (saves spec, ADR 0004).

mod lock;
mod meta;
mod open;
mod write;

use std::path::{Component, Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};

use app::saves::{NewSave, SaveError, SaveListing, SaveStore, Timestamp};
use diesel::prelude::*;
use diesel_migrations::{EmbeddedMigrations, MigrationHarness, embed_migrations};

use crate::schema::save_meta;
use crate::slug::{free_stem, slug};

pub use open::SqliteSave;

pub const MIGRATIONS: EmbeddedMigrations = embed_migrations!("migrations");

/// The extension of save files.
pub const EXTENSION: &str = "esmsave";
const TEMPORARY: &str = "tmp";
/// Held while a save is created: `.create.lock` in the folder.
const CREATION: &str = ".create";
/// A temporary save's rollback journal: `<temporary>-journal`.
const TEMPORARY_JOURNAL: &str = "tmp-journal";

/// Saves in one folder.
#[derive(Debug)]
pub struct SqliteSaveStore {
    dir: PathBuf,
}

static ATTEMPTS: AtomicU64 = AtomicU64::new(0);

impl SqliteSaveStore {
    /// The store for `dir`. Leftovers of crashed creations are removed.
    #[must_use]
    pub fn new(dir: PathBuf) -> Self {
        let store = Self { dir };
        store.remove_leftovers();
        store
    }

    fn path(&self, file: &str) -> PathBuf {
        self.dir.join(file)
    }

    /// The names in the folder that end in `.<extension>`, sorted.
    fn files(&self, extension: &str) -> Result<Vec<String>, SaveError> {
        let entries =
            std::fs::read_dir(&self.dir).map_err(|e| SaveError::Storage(e.to_string()))?;
        let mut files: Vec<String> = entries
            .filter_map(Result::ok)
            .filter(|entry| entry.file_type().is_ok_and(|t| t.is_file()))
            .filter_map(|entry| entry.file_name().into_string().ok())
            .filter(|name| Path::new(name).extension().is_some_and(|e| e == extension))
            .collect();
        files.sort();
        Ok(files)
    }

    /// Removes what crashed creations left: temporary saves no process holds,
    /// their rollback journals and lock files, and journals whose temporary
    /// save is already gone.
    fn remove_leftovers(&self) {
        for file in self.files(TEMPORARY).unwrap_or_default() {
            let path = self.path(&file);
            if lock::is_held(&path) {
                continue;
            }
            for leftover in [path.clone(), journal(&path), lock::lock_path(&path)] {
                let _ = std::fs::remove_file(leftover);
            }
        }
        for file in self.files(TEMPORARY_JOURNAL).unwrap_or_default() {
            let path = self.path(&file);
            let owner = path.with_extension(TEMPORARY);
            if !owner.exists() {
                let _ = std::fs::remove_file(path);
            }
        }
    }

    /// The display names of every save in the folder, whatever its version.
    fn names(&self) -> Result<Vec<String>, SaveError> {
        Ok(self
            .files(EXTENSION)?
            .iter()
            .filter_map(|file| meta::connect(&self.path(file)).ok())
            .filter_map(|mut connection| meta::read_name(&mut connection))
            .collect())
    }
}

/// SQLite's rollback journal of `path`.
fn journal(path: &Path) -> PathBuf {
    let mut name = path.as_os_str().to_owned();
    name.push("-journal");
    PathBuf::from(name)
}

/// Whether `file` names a save directly in the folder: one plain component
/// with the save extension. This rules out `../x`, `a/b` and, on Windows,
/// drive-relative names such as `C:x.esmsave`.
fn is_save_name(file: &str) -> bool {
    let path = Path::new(file);
    let mut components = path.components();
    matches!(
        (components.next(), components.next()),
        (Some(Component::Normal(_)), None)
    ) && path.extension().is_some_and(|e| e == EXTENSION)
}

impl SaveStore for SqliteSaveStore {
    type Save = SqliteSave;

    fn create(&self, save: NewSave) -> Result<String, SaveError> {
        // One creation at a time in the folder, from reading the names to
        // moving the save into place, so two processes can't both take a
        // free name (SAVE-010). The use case checks names earlier, to report
        // the problem with the others; this is the check that guarantees it.
        let _creating = lock::wait(&self.path(CREATION))?;
        // Kept for the commit's error, after writing has taken the save.
        let name = save.meta.name.clone();
        let wanted = name.to_lowercase();
        if self
            .names()?
            .iter()
            .any(|taken| taken.to_lowercase() == wanted)
        {
            return Err(SaveError::NameTaken(name));
        }
        let stem = free_stem(&slug(&name), |stem| {
            self.path(&format!("{stem}.{EXTENSION}")).exists()
        });
        let file = format!("{stem}.{EXTENSION}");
        let attempt = ATTEMPTS.fetch_add(1, Ordering::Relaxed);
        let temporary = self.path(&format!(
            "{stem}.{}-{attempt}.{TEMPORARY}",
            std::process::id()
        ));

        // Held while the temporary file exists, so another process's cleanup
        // never removes a save still being written.
        let held = lock::acquire(&temporary)?;
        let written = write::write_new(&temporary, save)
            .and_then(|()| write::commit(&temporary, &self.path(&file), &name));
        if written.is_err() {
            let _ = std::fs::remove_file(&temporary);
            let _ = std::fs::remove_file(journal(&temporary));
        }
        drop(held);
        let _ = std::fs::remove_file(lock::lock_path(&temporary));
        written.map(|()| file)
    }

    fn list(&self) -> Result<Vec<SaveListing>, SaveError> {
        let mut listings: Vec<SaveListing> = self
            .files(EXTENSION)?
            .into_iter()
            .map(|file| {
                let path = self.path(&file);
                let save = meta::connect(&path)
                    .map_err(|_| app::saves::Damage::NotASave)
                    .and_then(|mut connection| meta::read_meta(&mut connection));
                SaveListing {
                    in_use: lock::is_held(&path),
                    file,
                    save,
                }
            })
            .collect();
        listings.sort_by(|a, b| match (&a.save, &b.save) {
            (Ok(x), Ok(y)) => y
                .last_played_at
                .cmp(&x.last_played_at)
                .then_with(|| x.name.to_lowercase().cmp(&y.name.to_lowercase()))
                .then_with(|| x.name.cmp(&y.name))
                .then_with(|| a.file.cmp(&b.file)),
            (Ok(_), Err(_)) => std::cmp::Ordering::Less,
            (Err(_), Ok(_)) => std::cmp::Ordering::Greater,
            (Err(_), Err(_)) => a.file.cmp(&b.file),
        });
        Ok(listings)
    }

    fn open(&self, file: &str, now: Timestamp) -> Result<SqliteSave, SaveError> {
        let path = self.path(file);
        if !is_save_name(file) || !path.is_file() {
            return Err(SaveError::NotFound(file.to_owned()));
        }
        let lock = lock::acquire(&path)?;
        let mut connection = meta::connect(&path).map_err(|_| SaveError::NotASave)?;
        // The version check needs nothing but Diesel's migrations table; only
        // then is the save migrated and its metadata read.
        if meta::is_newer(&mut connection)? {
            return Err(SaveError::NewerVersion);
        }
        connection
            .run_pending_migrations(MIGRATIONS)
            .map_err(|e| SaveError::Storage(e.to_string()))?;
        diesel::update(save_meta::table)
            .set(save_meta::last_played_at.eq(now.0))
            .execute(&mut connection)
            .map_err(meta::storage)?;
        let meta = meta::read_meta(&mut connection)?;
        Ok(SqliteSave {
            connection,
            meta,
            _lock: lock,
        })
    }
}

#[cfg(test)]
mod tests;
