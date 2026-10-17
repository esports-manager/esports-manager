// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Connections, the version check, and reading `save_meta`.
//!
//! The metadata is read with plain SQL naming each column, in the order a
//! save from any version can answer: first the version check, which needs
//! only Diesel's migrations table, then the metadata. A save from an older
//! version is still listed, and a newer one is recognised as newer.

use std::path::Path;

use app::saves::{Damage, PackageRecord, SaveError, SaveMeta, Timestamp};
use diesel::migration::MigrationSource;
use diesel::prelude::*;
use diesel::query_dsl::methods::OrderDsl;
use diesel::sql_types::{BigInt, Binary, Text};
use diesel::sqlite::SqliteConnection;
use domain::rng::WorldSeed;

use super::MIGRATIONS;
use crate::rows;

/// How long a connection waits for another process's transaction. Saves are
/// kept exclusive by their lock file; this only covers short overlaps, such
/// as a listing reading a save while it is opened.
const BUSY_TIMEOUT_MS: u32 = 2_000;

/// Opens a connection with the game's settings.
pub(super) fn connect(path: &Path) -> Result<SqliteConnection, SaveError> {
    let url = path
        .to_str()
        .ok_or_else(|| SaveError::Storage(format!("{} is not a UTF-8 path", path.display())))?;
    let mut connection =
        SqliteConnection::establish(url).map_err(|e| SaveError::Storage(e.to_string()))?;
    for pragma in [
        format!("PRAGMA busy_timeout = {BUSY_TIMEOUT_MS}"),
        "PRAGMA foreign_keys = ON".to_owned(),
    ] {
        diesel::sql_query(pragma)
            .execute(&mut connection)
            .map_err(storage)?;
    }
    Ok(connection)
}

#[expect(clippy::needless_pass_by_value, reason = "passed to `map_err` by name")]
pub(super) fn storage(error: diesel::result::Error) -> SaveError {
    SaveError::Storage(error.to_string())
}

#[derive(QueryableByName)]
struct Version {
    #[diesel(sql_type = Text)]
    version: String,
}

/// Whether the save has a migration this version of the game doesn't know.
/// A file without Diesel's migrations table isn't a save.
pub(super) fn is_newer(connection: &mut SqliteConnection) -> Result<bool, Damage> {
    let applied: Vec<Version> =
        diesel::sql_query("SELECT version FROM __diesel_schema_migrations ORDER BY version")
            .load(connection)
            .map_err(|_| Damage::NotASave)?;
    let known: Vec<String> = MigrationSource::<diesel::sqlite::Sqlite>::migrations(&MIGRATIONS)
        .map_err(|_| Damage::NotASave)?
        .iter()
        .map(|migration| migration.name().version().to_string())
        .collect();
    Ok(applied.iter().any(|row| !known.contains(&row.version)))
}

/// The columns of `save_meta` every version has.
#[derive(QueryableByName)]
pub(super) struct MetaRow {
    #[diesel(sql_type = Text)]
    name: String,
    #[diesel(sql_type = Text)]
    manager_name: String,
    #[diesel(sql_type = Text)]
    team_id: String,
    #[diesel(sql_type = Text)]
    genre: String,
    #[diesel(sql_type = BigInt)]
    seed: i64,
    #[diesel(sql_type = Text)]
    game_version: String,
    #[diesel(sql_type = Text)]
    game_date: String,
    #[diesel(sql_type = BigInt)]
    created_at: i64,
    #[diesel(sql_type = BigInt)]
    last_played_at: i64,
}

#[derive(QueryableByName)]
struct PackageRow {
    #[diesel(sql_type = Text)]
    id: String,
    #[diesel(sql_type = Text)]
    version: String,
    #[diesel(sql_type = Binary)]
    content_hash: Vec<u8>,
}

/// The save's name, whatever its version, for name uniqueness.
pub(super) fn read_name(connection: &mut SqliteConnection) -> Option<String> {
    #[derive(QueryableByName)]
    struct Name {
        #[diesel(sql_type = Text)]
        name: String,
    }
    diesel::sql_query("SELECT name FROM save_meta WHERE id = 1")
        .get_result::<Name>(connection)
        .ok()
        .map(|row| row.name)
}

/// Reads `save_meta` without changing the file, checking that it is a save
/// this version of the game understands.
pub(super) fn read_meta(connection: &mut SqliteConnection) -> Result<SaveMeta, Damage> {
    if is_newer(connection)? {
        return Err(Damage::NewerVersion);
    }
    let row: MetaRow = diesel::sql_query(
        "SELECT name, manager_name, team_id, genre, seed, game_version, game_date, \
         created_at, last_played_at FROM save_meta WHERE id = 1",
    )
    .get_result(connection)
    .map_err(|_| Damage::NotASave)?;
    let packages: Vec<PackageRow> =
        diesel::sql_query("SELECT id, version, content_hash FROM packages ORDER BY position")
            .load(connection)
            .map_err(|_| Damage::NotASave)?;
    meta_from_rows(row, packages).map_err(|_| Damage::NotASave)
}

fn meta_from_rows(row: MetaRow, packages: Vec<PackageRow>) -> Result<SaveMeta, SaveError> {
    let MetaRow {
        name,
        manager_name,
        team_id,
        genre,
        seed,
        game_version,
        game_date,
        created_at,
        last_played_at,
    } = row;
    let packages = packages
        .into_iter()
        .map(
            |PackageRow {
                 id,
                 version,
                 content_hash,
             }| {
                let content_hash: [u8; 32] = content_hash
                    .try_into()
                    .map_err(|_| rows::corrupt("content hash", &id))?;
                Ok(PackageRecord {
                    id,
                    version,
                    content_hash,
                })
            },
        )
        .collect::<Result<_, SaveError>>()?;
    Ok(SaveMeta {
        name,
        manager_name,
        team: rows::id(&team_id)?,
        genre: rows::genre_from_db(&genre)?,
        seed: WorldSeed::new(rows::seed_from_db(seed)),
        game_version,
        game_date: rows::date(&game_date)?,
        created_at: Timestamp(created_at),
        last_played_at: Timestamp(last_played_at),
        packages,
    })
}

/// Every query that returns a collection goes through here, so its order is
/// always spelled out (ADR 0003). Review checks that no query bypasses it.
pub(super) fn load_ordered<'q, Q, O, T>(
    connection: &mut SqliteConnection,
    query: Q,
    order: O,
) -> QueryResult<Vec<T>>
where
    O: diesel::Expression,
    Q: OrderDsl<O>,
    Q::Output: diesel::query_dsl::LoadQuery<'q, SqliteConnection, T>,
{
    query.order(order).load(connection)
}
