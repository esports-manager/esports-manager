// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! A save this process holds open, and the queries the screens use.

use std::collections::BTreeMap;
use std::fs::File;

use app::content::ContentText;
use app::saves::{OpenSave, SaveError, SaveMeta};
use diesel::prelude::*;
use diesel::sqlite::SqliteConnection;
use domain::id::ContentId;
use domain::world::{Competition, Nationality, Region, Team};
use esports::moba::attributes::OverallAttribute;
use esports::moba::roles::RoleSet;
use esports::moba::world::Player;

use super::meta::{load_ordered, storage};
use crate::rows::{
    self, CompetitionRow, CompetitionTeamRow, NationalityRow, PlayerRow, RegionNationalityRow,
    RegionRow, RoleRow, TeamRow, TextRow,
};
use crate::schema::{
    competition_teams, competitions, content_texts, nationalities, players, region_nationalities,
    regions, roles, teams,
};

/// A save this process holds open. Its lock is released when it is dropped.
pub struct SqliteSave {
    pub(super) connection: SqliteConnection,
    pub(super) meta: SaveMeta,
    /// Held for as long as the save is open (saves spec: one process at a time).
    pub(super) _lock: File,
}

impl OpenSave for SqliteSave {
    fn meta(&self) -> &SaveMeta {
        &self.meta
    }

    fn team(&mut self, id: &ContentId) -> Result<Option<Team>, SaveError> {
        teams::table
            .filter(teams::id.eq(id.as_str()))
            .select(TeamRow::as_select())
            .first(&mut self.connection)
            .optional()
            .map_err(storage)?
            .map(TeamRow::into_domain)
            .transpose()
    }

    fn players_of(&mut self, team: &ContentId) -> Result<Vec<Player>, SaveError> {
        let query = players::table
            .filter(players::team_id.eq(team.as_str()))
            .select(PlayerRow::as_select());
        let rows: Vec<PlayerRow> =
            load_ordered(&mut self.connection, query, players::position.asc()).map_err(storage)?;
        rows.into_iter().map(PlayerRow::into_domain).collect()
    }

    fn player(&mut self, id: &ContentId) -> Result<Option<Player>, SaveError> {
        players::table
            .filter(players::id.eq(id.as_str()))
            .select(PlayerRow::as_select())
            .first(&mut self.connection)
            .optional()
            .map_err(storage)?
            .map(PlayerRow::into_domain)
            .transpose()
    }

    fn roles(&mut self) -> Result<RoleSet, SaveError> {
        let rows: Vec<RoleRow> = load_ordered(
            &mut self.connection,
            roles::table.select(RoleRow::as_select()),
            roles::position.asc(),
        )
        .map_err(storage)?;
        let definitions = rows
            .into_iter()
            .map(|row| {
                let (id, weights) = row.into_parts()?;
                Ok((
                    id,
                    OverallAttribute::ALL
                        .into_iter()
                        .zip(weights)
                        .collect::<BTreeMap<_, _>>(),
                ))
            })
            .collect::<Result<Vec<_>, SaveError>>()?;
        RoleSet::new(definitions).map_err(|_| rows::corrupt("role set", "weights"))
    }

    fn regions(&mut self) -> Result<Vec<Region>, SaveError> {
        let region_rows: Vec<RegionRow> = load_ordered(
            &mut self.connection,
            regions::table.select(RegionRow::as_select()),
            regions::position.asc(),
        )
        .map_err(storage)?;
        let mix_rows: Vec<RegionNationalityRow> = load_ordered(
            &mut self.connection,
            region_nationalities::table.select(RegionNationalityRow::as_select()),
            (
                region_nationalities::region_id.asc(),
                region_nationalities::nationality_id.asc(),
            ),
        )
        .map_err(storage)?;
        region_rows
            .into_iter()
            .map(
                |RegionRow {
                     id,
                     position: _,
                     level,
                 }| {
                    let nationalities = mix_rows
                        .iter()
                        .filter(|mix| mix.region_id == id)
                        .map(|mix| {
                            let weight = u32::try_from(mix.weight)
                                .map_err(|_| rows::corrupt("weight", &mix.weight.to_string()))?;
                            Ok((rows::id(&mix.nationality_id)?, weight))
                        })
                        .collect::<Result<_, SaveError>>()?;
                    Ok(Region {
                        id: rows::id(&id)?,
                        level,
                        nationalities,
                    })
                },
            )
            .collect()
    }

    fn nationalities(&mut self) -> Result<Vec<Nationality>, SaveError> {
        let rows: Vec<NationalityRow> = load_ordered(
            &mut self.connection,
            nationalities::table.select(NationalityRow::as_select()),
            nationalities::position.asc(),
        )
        .map_err(storage)?;
        rows.into_iter().map(NationalityRow::into_domain).collect()
    }

    fn competitions(&mut self) -> Result<Vec<Competition>, SaveError> {
        let competition_rows: Vec<CompetitionRow> = load_ordered(
            &mut self.connection,
            competitions::table.select(CompetitionRow::as_select()),
            competitions::position.asc(),
        )
        .map_err(storage)?;
        let entrants: Vec<CompetitionTeamRow> = load_ordered(
            &mut self.connection,
            competition_teams::table.select(CompetitionTeamRow::as_select()),
            (
                competition_teams::competition_id.asc(),
                competition_teams::position.asc(),
            ),
        )
        .map_err(storage)?;
        competition_rows
            .into_iter()
            .map(
                |CompetitionRow {
                     id,
                     position: _,
                     region_id,
                 }| {
                    let teams = entrants
                        .iter()
                        .filter(|entrant| entrant.competition_id == id)
                        .map(|entrant| rows::id(&entrant.team_id))
                        .collect::<Result<_, _>>()?;
                    Ok(Competition {
                        id: rows::id(&id)?,
                        region: rows::id(&region_id)?,
                        teams,
                    })
                },
            )
            .collect()
    }

    fn texts(&mut self) -> Result<Vec<ContentText>, SaveError> {
        let rows: Vec<TextRow> = load_ordered(
            &mut self.connection,
            content_texts::table.select(TextRow::as_select()),
            (content_texts::locale.asc(), content_texts::file.asc()),
        )
        .map_err(storage)?;
        Ok(rows
            .into_iter()
            .map(
                |TextRow {
                     locale,
                     file,
                     source,
                 }| ContentText {
                    locale,
                    file,
                    source,
                },
            )
            .collect())
    }
}
