// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Loading and validation of `.esm` content packages (ADR 0005, packages
//! spec).
//!
//! A package goes through four steps: its files are read ([`PackageFiles`]),
//! each file is parsed into its definition type, each definition is converted
//! into its domain type, and the whole is checked across entities. Every
//! problem from every step is reported together.

mod check;
mod convert;
pub mod defs;
mod files;
mod parse;
pub mod schemas;

use std::path::Path;

use esports::moba::world::WorldTemplate;

pub use app::content::{Manifest, NameKind, Package, PackageError, Problem};
pub use files::PackageFiles;

use convert::Located;
use parse::{Entry, MANIFEST, WORLD};

/// Loads the package in the directory `root`.
///
/// # Errors
///
/// Every problem found, sorted by file.
pub fn load(root: &Path) -> Result<Package, Vec<PackageError>> {
    let unreadable = |file: String, error: &std::io::Error| {
        PackageError::new(
            file,
            "",
            Problem::Unreadable {
                reason: error.to_string(),
            },
        )
    };
    let (files, problems) = PackageFiles::read_dir_reporting(root)
        .map_err(|error| vec![unreadable(root.display().to_string(), &error)])?;
    if !problems.is_empty() {
        return Err(problems
            .iter()
            .map(|(file, error)| unreadable(file.clone(), error))
            .collect());
    }
    load_files(&files)
}

/// Loads a package from files in memory.
///
/// # Errors
///
/// Every problem found, sorted by file.
pub fn load_files(files: &PackageFiles) -> Result<Package, Vec<PackageError>> {
    let mut errors = Vec::new();
    let parsed = parse::parse(files, &mut errors);
    let declared = check::declared(&parsed, &mut errors);

    let manifest = required(&parsed.present, parsed.manifest, MANIFEST, &mut errors)
        .and_then(|entry| convert::manifest(entry, &mut errors));
    let world = required(&parsed.present, parsed.world, WORLD, &mut errors)
        .and_then(|entry| convert::world(entry, &mut errors));
    let regions = convert::all(parsed.regions, &mut errors, convert::region);
    let nationalities = convert::all(parsed.nationalities, &mut errors, convert::nationality);
    let name_pools = convert::all(parsed.name_pools, &mut errors, convert::name_pool);
    let nicknames = convert::all(parsed.nicknames, &mut errors, convert::nickname_pool);
    let competitions = convert::all(parsed.competitions, &mut errors, convert::competition);
    let teams = convert::all(parsed.teams, &mut errors, convert::team);
    let players = convert::all(parsed.players, &mut errors, convert::player);
    let roles = exactly_one(parsed.role_sets, "roles/", &mut errors, convert::role_set);
    let generation = exactly_one(
        parsed.generations,
        "generation/",
        &mut errors,
        convert::generation,
    );

    check::check(
        &declared,
        &parsed.texts,
        &check::Content {
            regions: &regions,
            nationalities: &nationalities,
            name_pools: &name_pools,
            nicknames: &nicknames,
            competitions: &competitions,
            teams: &teams,
            players: &players,
            roles: roles.as_ref(),
            generation: generation.as_ref(),
            start_date: world.map(|world| world.start_date),
        },
        &mut errors,
    );

    let (Some(manifest), Some(world), Some(roles), Some(generation), true) =
        (manifest, world, roles, generation, errors.is_empty())
    else {
        errors.sort_by(|a, b| a.file.cmp(&b.file));
        return Err(errors);
    };
    let (roles, roster) = roles.value;
    Ok(Package {
        manifest,
        content_hash: files.content_hash(),
        template: WorldTemplate {
            settings: world,
            regions: values(regions),
            nationalities: values(nationalities),
            name_pools: values(name_pools),
            nicknames: merge_nicknames(nicknames),
            competitions: values(competitions),
            teams: values(teams),
            players: values(players),
            roles,
            roster,
            generation: generation.value,
        },
        texts: parsed.texts,
    })
}

/// A required root file. It is missing only if the package has no such
/// file; one that is there but broken has already been reported.
fn required<T>(
    present: &[&str],
    entry: Option<Entry<T>>,
    file: &'static str,
    errors: &mut Vec<PackageError>,
) -> Option<Entry<T>> {
    if entry.is_none() && !present.contains(&file) {
        errors.push(PackageError::new(file, "", Problem::MissingFile));
    }
    entry
}

/// The one entity of a kind a package must define exactly once. Every
/// entity is converted anyway, so its own problems are reported too.
fn exactly_one<D, V>(
    entries: Vec<Entry<D>>,
    folder: &str,
    errors: &mut Vec<PackageError>,
    convert: impl Fn(Entry<D>, &mut Vec<PackageError>) -> Option<Located<V>>,
) -> Option<Located<V>> {
    let count = entries.len();
    let wrong_count = (count != 1).then(|| {
        let file = entries.get(1).map_or(folder, |entry| entry.file.as_str());
        PackageError::new(
            file,
            "",
            Problem::WrongCount {
                folder: folder.to_owned(),
                count,
            },
        )
    });
    let converted = convert::all(entries, errors, convert);
    if let Some(error) = wrong_count {
        errors.push(error);
        return None;
    }
    converted.into_iter().next()
}

/// The package in a directory, as the application's content source.
#[derive(Debug)]
pub struct PackageDir(pub std::path::PathBuf);

impl app::content::ContentSource for PackageDir {
    fn load(&self) -> Result<Package, Vec<PackageError>> {
        load(&self.0)
    }
}

fn values<T>(located: Vec<Located<T>>) -> Vec<T> {
    located.into_iter().map(|located| located.value).collect()
}

fn merge_nicknames(pools: Vec<Located<Vec<String>>>) -> Vec<String> {
    let mut seen = std::collections::BTreeSet::new();
    pools
        .into_iter()
        .flat_map(|pool| pool.value)
        .filter(|nickname| seen.insert(nickname.to_lowercase()))
        .collect()
}

#[cfg(test)]
mod tests;
