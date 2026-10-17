// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Writing a new save: the whole world in one transaction, into a temporary
//! file that is then moved into place without ever replacing a file.

use std::path::Path;

use app::content::ContentText;
use app::saves::{NewSave, SaveError, SaveMeta};
use diesel::prelude::*;
use diesel::sqlite::SqliteConnection;
use diesel_migrations::MigrationHarness;
use esports::moba::roles::RoleSet;
use esports::moba::world::{Player, World};

use super::MIGRATIONS;
use super::meta::{connect, storage};
use crate::rows::{
    self, CompetitionRow, CompetitionTeamRow, NationalityRow, PackageRow, PlayerRow,
    RegionNationalityRow, RegionRow, RoleRow, SaveMetaRow, TeamRow, TextRow,
};
use crate::schema::{
    competition_teams, competitions, content_texts, nationalities, packages, players,
    region_nationalities, regions, roles, save_meta, teams,
};

/// A row conversion failed; Diesel's transaction needs its own error type.
fn to_query(error: SaveError) -> diesel::result::Error {
    diesel::result::Error::QueryBuilderError(Box::new(error))
}

pub(super) fn write_new(path: &Path, save: NewSave) -> Result<(), SaveError> {
    let mut connection = connect(path)?;
    connection
        .run_pending_migrations(MIGRATIONS)
        .map_err(|e| SaveError::Storage(e.to_string()))?;
    connection
        .transaction(|connection| insert_world(connection, save))
        .map_err(storage)
}

fn insert_world(connection: &mut SqliteConnection, save: NewSave) -> QueryResult<()> {
    let NewSave { meta, world, texts } = save;
    insert_places(connection, &world)?;
    insert_teams(connection, &world)?;
    insert_people(connection, &world.roles, world.players)?;
    let SaveMeta {
        name,
        manager_name,
        team,
        genre,
        seed,
        game_version,
        game_date,
        created_at,
        last_played_at,
        packages: package_records,
    } = meta;
    diesel::insert_into(save_meta::table)
        .values(SaveMetaRow {
            id: 1,
            name,
            manager_name,
            team_id: team.to_string(),
            genre: rows::genre_to_db(genre).to_owned(),
            seed: rows::seed_to_db(seed.value()),
            game_version,
            game_date: game_date.to_string(),
            created_at: created_at.0,
            last_played_at: last_played_at.0,
        })
        .execute(connection)?;

    let package_rows = package_records
        .into_iter()
        .enumerate()
        .map(|(index, record)| {
            Ok(PackageRow {
                id: record.id,
                position: rows::position(index)?,
                version: record.version,
                content_hash: record.content_hash.to_vec(),
            })
        })
        .collect::<Result<Vec<_>, SaveError>>()
        .map_err(to_query)?;
    diesel::insert_into(packages::table)
        .values(&package_rows)
        .execute(connection)?;

    let text_rows: Vec<TextRow> = texts
        .into_iter()
        .map(
            |ContentText {
                 locale,
                 file,
                 source,
             }| TextRow {
                locale,
                file,
                source,
            },
        )
        .collect();
    diesel::insert_into(content_texts::table)
        .values(&text_rows)
        .execute(connection)?;
    Ok(())
}

fn insert_places(connection: &mut SqliteConnection, world: &World) -> QueryResult<()> {
    let nationality_rows = world
        .nationalities
        .iter()
        .enumerate()
        .map(|(index, nationality)| {
            Ok(NationalityRow {
                id: nationality.id.to_string(),
                position: rows::position(index)?,
                code: nationality.code.as_str().to_owned(),
                name_order: rows::name_order_to_db(nationality.name_order).to_owned(),
            })
        })
        .collect::<Result<Vec<_>, SaveError>>()
        .map_err(to_query)?;
    diesel::insert_into(nationalities::table)
        .values(&nationality_rows)
        .execute(connection)?;

    let mut region_rows = Vec::new();
    let mut mix_rows = Vec::new();
    for (index, region) in world.regions.iter().enumerate() {
        region_rows.push(RegionRow {
            id: region.id.to_string(),
            position: rows::position(index).map_err(to_query)?,
            level: region.level,
        });
        for (nationality, weight) in &region.nationalities {
            mix_rows.push(RegionNationalityRow {
                region_id: region.id.to_string(),
                nationality_id: nationality.to_string(),
                weight: i32::try_from(*weight)
                    .map_err(|_| to_query(rows::corrupt("weight", &weight.to_string())))?,
            });
        }
    }
    diesel::insert_into(regions::table)
        .values(&region_rows)
        .execute(connection)?;
    diesel::insert_into(region_nationalities::table)
        .values(&mix_rows)
        .execute(connection)?;
    Ok(())
}

fn insert_teams(connection: &mut SqliteConnection, world: &World) -> QueryResult<()> {
    let team_rows = world
        .teams
        .iter()
        .enumerate()
        .map(|(index, team)| TeamRow::from_domain(team, index))
        .collect::<Result<Vec<_>, _>>()
        .map_err(to_query)?;
    diesel::insert_into(teams::table)
        .values(&team_rows)
        .execute(connection)?;

    let mut competition_rows = Vec::new();
    let mut entrant_rows = Vec::new();
    for (index, competition) in world.competitions.iter().enumerate() {
        competition_rows.push(CompetitionRow {
            id: competition.id.to_string(),
            position: rows::position(index).map_err(to_query)?,
            region_id: competition.region.to_string(),
        });
        for (slot, team) in competition.teams.iter().enumerate() {
            entrant_rows.push(CompetitionTeamRow {
                competition_id: competition.id.to_string(),
                position: rows::position(slot).map_err(to_query)?,
                team_id: team.to_string(),
            });
        }
    }
    diesel::insert_into(competitions::table)
        .values(&competition_rows)
        .execute(connection)?;
    diesel::insert_into(competition_teams::table)
        .values(&entrant_rows)
        .execute(connection)?;
    Ok(())
}

fn insert_people(
    connection: &mut SqliteConnection,
    roles: &RoleSet,
    players: Vec<Player>,
) -> QueryResult<()> {
    let role_rows = roles
        .roles()
        .iter()
        .enumerate()
        .map(|(index, role)| RoleRow::from_domain(role, index))
        .collect::<Result<Vec<_>, _>>()
        .map_err(to_query)?;
    diesel::insert_into(roles::table)
        .values(&role_rows)
        .execute(connection)?;

    let player_rows = players
        .into_iter()
        .enumerate()
        .map(|(index, player)| PlayerRow::from_domain(player, index))
        .collect::<Result<Vec<_>, _>>()
        .map_err(to_query)?;
    diesel::insert_into(players::table)
        .values(&player_rows)
        .execute(connection)?;

    Ok(())
}

/// Moves a finished save into place without ever replacing a file.
pub(super) fn commit(temporary: &Path, target: &Path, name: &str) -> Result<(), SaveError> {
    commit_with(
        |from, to| std::fs::hard_link(from, to),
        temporary,
        target,
        name,
    )
}

/// `commit`, with the hard link as a parameter so the fallback is testable.
pub(super) fn commit_with(
    link: impl Fn(&Path, &Path) -> std::io::Result<()>,
    temporary: &Path,
    target: &Path,
    name: &str,
) -> Result<(), SaveError> {
    let taken = || SaveError::NameTaken(name.to_owned());
    // A hard link fails if the target exists, so it never replaces a save.
    match link(temporary, target) {
        Ok(()) => {
            let _ = std::fs::remove_file(temporary);
            return Ok(());
        }
        Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => return Err(taken()),
        Err(_) => {}
    }
    // Some file systems (FAT on a USB stick, say) have no hard links. Creating
    // the target with `create_new` claims the name atomically, so a save that
    // appears in the meantime is never replaced; the bytes are then copied.
    // The target's lock is held meanwhile, so nobody opens a half-copied save.
    let _copying = super::lock::acquire(target)?;
    let mut destination = std::fs::OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(target)
        .map_err(|error| {
            if error.kind() == std::io::ErrorKind::AlreadyExists {
                taken()
            } else {
                SaveError::Storage(error.to_string())
            }
        })?;
    let copied = std::fs::File::open(temporary)
        .and_then(|mut source| std::io::copy(&mut source, &mut destination))
        .and_then(|_| destination.sync_all());
    drop(destination);
    if let Err(error) = copied {
        let _ = std::fs::remove_file(target);
        return Err(SaveError::Storage(error.to_string()));
    }
    let _ = std::fs::remove_file(temporary);
    Ok(())
}
