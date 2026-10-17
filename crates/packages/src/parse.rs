// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Classifying a package's files and deserializing each one into its
//! [`defs`](crate::defs) type. Every problem is collected; nothing stops at
//! the first error.

use app::content::ContentText;
use serde::de::DeserializeOwned;
use serde_json::value::RawValue;

use crate::defs::{
    CompetitionDef, GenerationDef, ManifestDef, NamePoolDef, NationalityDef, NicknamePoolDef,
    PlayerDef, RegionDef, RoleSetDef, TeamDef, WorldDef,
};
use crate::files::PackageFiles;
use app::content::{PackageError, Problem};

pub const MANIFEST: &str = "manifest.json";
pub const WORLD: &str = "world.json";
const LOCALES: &str = "locales";

/// The content-type folders and the id kind each one holds.
pub const FOLDERS: [(&str, &str); 9] = [
    ("competitions", "competition"),
    ("generation", "generation"),
    ("name-pools", "name_pool"),
    ("nationalities", "nationality"),
    ("nicknames", "nickname_pool"),
    ("players", "player"),
    ("regions", "region"),
    ("roles", "role_set"),
    ("teams", "team"),
];

/// One entity and where it came from.
#[derive(Debug)]
pub struct Entry<T> {
    pub file: String,
    /// `[2]` for the third entity of a list file, empty for a single object.
    pub path: String,
    pub def: T,
}

impl<T> Entry<T> {
    /// The path of `field` inside this entity.
    pub fn at(&self, field: &str) -> String {
        join(&self.path, field)
    }
}

#[derive(Debug, Default)]
pub struct Parsed {
    pub manifest: Option<Entry<ManifestDef>>,
    pub world: Option<Entry<WorldDef>>,
    pub competitions: Vec<Entry<CompetitionDef>>,
    pub generations: Vec<Entry<GenerationDef>>,
    pub name_pools: Vec<Entry<NamePoolDef>>,
    pub nationalities: Vec<Entry<NationalityDef>>,
    pub nicknames: Vec<Entry<NicknamePoolDef>>,
    pub players: Vec<Entry<PlayerDef>>,
    pub regions: Vec<Entry<RegionDef>>,
    pub role_sets: Vec<Entry<RoleSetDef>>,
    pub teams: Vec<Entry<TeamDef>>,
    pub texts: Vec<ContentText>,
    /// The required root files that exist, whether or not they parsed.
    pub present: Vec<&'static str>,
}

pub fn parse(files: &PackageFiles, errors: &mut Vec<PackageError>) -> Parsed {
    let mut parsed = Parsed::default();
    let mut unknown_folders = Vec::new();
    for (path, contents) in files.iter() {
        let (folder, rest) = path.split_once('/').unwrap_or(("", path));
        match folder {
            "" if path == MANIFEST => {
                parsed.present.push(MANIFEST);
                parsed.manifest = single(path, contents, errors);
            }
            "" if path == WORLD => {
                parsed.present.push(WORLD);
                parsed.world = single(path, contents, errors);
            }
            "" => errors.push(PackageError::new(path, "", Problem::UnexpectedFile)),
            LOCALES => text(path, rest, contents, &mut parsed, errors),
            _ if FOLDERS.iter().any(|(name, _)| *name == folder) => {
                if !has_extension(path, "json") {
                    errors.push(PackageError::new(path, "", Problem::UnexpectedFile));
                    continue;
                }
                entities_into(folder, path, contents, &mut parsed, errors);
            }
            _ => {
                if !unknown_folders.contains(&folder) {
                    unknown_folders.push(folder);
                    errors.push(PackageError::new(
                        format!("{folder}/"),
                        "",
                        Problem::UnknownFolder,
                    ));
                }
            }
        }
    }
    parsed
}

fn entities_into(
    folder: &str,
    path: &str,
    contents: &[u8],
    parsed: &mut Parsed,
    errors: &mut Vec<PackageError>,
) {
    match folder {
        "competitions" => parsed.competitions.extend(entities(path, contents, errors)),
        "generation" => parsed.generations.extend(entities(path, contents, errors)),
        "name-pools" => parsed.name_pools.extend(entities(path, contents, errors)),
        "nationalities" => parsed
            .nationalities
            .extend(entities(path, contents, errors)),
        "nicknames" => parsed.nicknames.extend(entities(path, contents, errors)),
        "players" => parsed.players.extend(entities(path, contents, errors)),
        "regions" => parsed.regions.extend(entities(path, contents, errors)),
        "roles" => parsed.role_sets.extend(entities(path, contents, errors)),
        _ => parsed.teams.extend(entities(path, contents, errors)),
    }
}

fn text(
    path: &str,
    rest: &str,
    contents: &[u8],
    parsed: &mut Parsed,
    errors: &mut Vec<PackageError>,
) {
    let Some((locale, _)) = rest.split_once('/') else {
        errors.push(PackageError::new(path, "", Problem::UnexpectedFile));
        return;
    };
    if !has_extension(path, "ftl") {
        errors.push(PackageError::new(path, "", Problem::UnexpectedFile));
        return;
    }
    match String::from_utf8(contents.to_vec()) {
        Ok(source) => parsed.texts.push(ContentText {
            locale: locale.to_owned(),
            file: path.to_owned(),
            // Fluent doesn't expect the byte-order mark some editors add.
            source: source
                .strip_prefix('\u{feff}')
                .unwrap_or(&source)
                .to_owned(),
        }),
        Err(_) => errors.push(PackageError::new(path, "", Problem::NotUtf8)),
    }
}

/// Extensions are matched exactly: `Team.JSON` is a stray file, not content.
fn has_extension(path: &str, extension: &str) -> bool {
    std::path::Path::new(path)
        .extension()
        .is_some_and(|found| found == extension)
}

/// The text of a JSON file, without the byte-order mark some editors add.
fn json_text<'a>(
    path: &str,
    contents: &'a [u8],
    errors: &mut Vec<PackageError>,
) -> Option<&'a str> {
    let Ok(text) = std::str::from_utf8(contents) else {
        errors.push(PackageError::new(path, "", Problem::NotUtf8));
        return None;
    };
    let text = text.strip_prefix('\u{feff}').unwrap_or(text);
    // Syntax first, for the whole file, so a list with a broken element is
    // reported once, with its position.
    if let Err(error) = serde_json::from_str::<serde::de::IgnoredAny>(text) {
        errors.push(PackageError::new(
            path,
            "",
            Problem::Syntax {
                line: error.line(),
                column: error.column(),
            },
        ));
        return None;
    }
    Some(text)
}

/// A file that must hold one object, such as the manifest.
fn single<T: DeserializeOwned>(
    path: &str,
    contents: &[u8],
    errors: &mut Vec<PackageError>,
) -> Option<Entry<T>> {
    let text = json_text(path, contents, errors)?;
    if !text.trim_start().starts_with('{') {
        errors.push(PackageError::new(path, "", Problem::NotAnEntity));
        return None;
    }
    entity(path, String::new(), text, errors)
}

/// A content file: one object, or a list of them.
fn entities<T: DeserializeOwned>(
    path: &str,
    contents: &[u8],
    errors: &mut Vec<PackageError>,
) -> Vec<Entry<T>> {
    let Some(text) = json_text(path, contents, errors) else {
        return Vec::new();
    };
    match text.trim_start().chars().next() {
        Some('{') => entity(path, String::new(), text, errors)
            .into_iter()
            .collect(),
        Some('[') => {
            // Each element is typed from its own text, not from a parsed
            // value, so a key repeated inside it is reported, not collapsed.
            let items: Vec<Box<RawValue>> = serde_json::from_str(text).unwrap_or_default();
            items
                .iter()
                .enumerate()
                .filter_map(|(index, item)| entity(path, format!("[{index}]"), item.get(), errors))
                .collect()
        }
        _ => {
            errors.push(PackageError::new(path, "", Problem::NotAnEntity));
            Vec::new()
        }
    }
}

fn entity<T: DeserializeOwned>(
    path: &str,
    prefix: String,
    text: &str,
    errors: &mut Vec<PackageError>,
) -> Option<Entry<T>> {
    let mut deserializer = serde_json::Deserializer::from_str(text);
    match serde_path_to_error::deserialize::<_, T>(&mut deserializer) {
        Ok(def) => Some(Entry {
            file: path.to_owned(),
            path: prefix,
            def,
        }),
        Err(error) => {
            let inner = error.path().to_string();
            let at = if inner == "." {
                prefix
            } else {
                join(&prefix, &inner)
            };
            errors.push(PackageError::new(path, at, classify(&error.into_inner())));
            None
        }
    }
}

/// Turns serde's description of a problem into a typed one where it can.
fn classify(error: &serde_json::Error) -> Problem {
    let message = error.to_string();
    let quoted = |prefix: &str| {
        message
            .strip_prefix(prefix)
            .and_then(|rest| rest.split_once('`'))
            .map(|(name, _)| name.to_owned())
    };
    if let Some(field) = quoted("unknown field `") {
        Problem::UnknownField { field }
    } else if let Some(field) = quoted("duplicate field `") {
        Problem::DuplicateField { field }
    } else if let Some(field) = quoted("missing field `") {
        Problem::MissingField { field }
    } else {
        Problem::InvalidValue { detail: message }
    }
}

/// `[2]` + `reputation` → `[2].reputation`; an empty side is dropped.
pub fn join(prefix: &str, field: &str) -> String {
    match (prefix.is_empty(), field.is_empty()) {
        (_, true) => prefix.to_owned(),
        (true, false) => field.to_owned(),
        (false, false) if field.starts_with('[') => format!("{prefix}{field}"),
        (false, false) => format!("{prefix}.{field}"),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn parse_one(path: &str, contents: &str) -> (Parsed, Vec<PackageError>) {
        let mut files = PackageFiles::new();
        files.insert(path, contents);
        let mut errors = Vec::new();
        let parsed = parse(&files, &mut errors);
        (parsed, errors)
    }

    const TEAM: &str = r##"{"id": "team:a", "region": "region:r", "tag": "AAA",
        "colours": ["#000000", "#FFFFFF"], "reputation": 50}"##;

    #[test]
    fn a_file_can_hold_one_entity_or_a_list() {
        // spec: PKG-002
        // Given
        let mut files = PackageFiles::new();
        files.insert("teams/a.json", TEAM);
        files.insert("teams/more.json", format!("[{TEAM}, {TEAM}]"));
        let mut errors = Vec::new();
        // When
        let parsed = parse(&files, &mut errors);
        // Then
        assert_eq!(errors, []);
        assert_eq!(parsed.teams.len(), 3);
        let paths: Vec<(&str, &str)> = parsed
            .teams
            .iter()
            .map(|entry| (entry.file.as_str(), entry.path.as_str()))
            .collect();
        assert_eq!(
            paths,
            [
                ("teams/a.json", ""),
                ("teams/more.json", "[0]"),
                ("teams/more.json", "[1]")
            ]
        );
    }

    #[test]
    fn unknown_fields_are_errors_with_their_path() {
        // spec: PKG-006
        // Given
        let typo = TEAM.replace("\"reputation\"", "\"reputaton\"");
        let contents = format!("[{TEAM}, {TEAM}, {typo}]");
        // When
        let (_, errors) = parse_one("teams/all.json", &contents);
        // Then
        assert_eq!(
            errors,
            [PackageError::new(
                "teams/all.json",
                "[2].reputaton",
                Problem::UnknownField {
                    field: "reputaton".to_owned()
                }
            )]
        );
    }

    #[test]
    fn unknown_top_level_folders_are_errors() {
        // spec: PKG-007
        // Given
        let mut files = PackageFiles::new();
        files.insert("team/a.json", TEAM);
        files.insert("team/b.json", TEAM);
        files.insert("teams/a.json", TEAM);
        let mut errors = Vec::new();
        // When
        parse(&files, &mut errors);
        // Then
        assert_eq!(
            errors,
            [PackageError::new("team/", "", Problem::UnknownFolder)]
        );
    }

    #[test]
    fn schema_pointers_are_accepted_on_single_objects() {
        // Given
        let contents = TEAM.replacen('{', r#"{"$schema": "../schemas/team.schema.json", "#, 1);
        // When
        let (parsed, errors) = parse_one("teams/a.json", &contents);
        // Then
        assert_eq!(errors, []);
        assert_eq!(
            parsed.teams[0].def.schema.as_deref(),
            Some("../schemas/team.schema.json")
        );
    }

    #[test]
    fn missing_fields_are_typed() {
        let (_, errors) = parse_one("teams/a.json", r#"{"id": "team:a"}"#);
        assert_eq!(
            errors[0].problem,
            Problem::MissingField {
                field: "region".to_owned()
            }
        );
        assert_eq!(errors[0].path, "");
    }

    #[test]
    fn nested_problems_keep_their_full_path() {
        let contents = TEAM.replace(r##"["#000000", "#FFFFFF"]"##, r##"["#000000", 7]"##);
        let (_, errors) = parse_one("teams/a.json", &format!("[{contents}]"));
        assert_eq!(errors[0].path, "[0].colours[1]");
        assert!(matches!(errors[0].problem, Problem::InvalidValue { .. }));
    }

    #[test]
    fn invalid_json_reports_its_position() {
        let (_, errors) = parse_one("teams/a.json", "{\n  \"id\": }");
        assert_eq!(
            errors,
            [PackageError::new(
                "teams/a.json",
                "",
                Problem::Syntax { line: 2, column: 9 }
            )]
        );
    }

    #[test]
    fn a_file_must_hold_objects() {
        let (_, errors) = parse_one("teams/a.json", "42");
        assert_eq!(
            errors,
            [PackageError::new("teams/a.json", "", Problem::NotAnEntity)]
        );
        let (_, errors) = parse_one(MANIFEST, "[]");
        assert_eq!(
            errors,
            [PackageError::new(MANIFEST, "", Problem::NotAnEntity)]
        );
    }

    #[test]
    fn stray_files_are_errors() {
        for path in [
            "README.md",
            "teams/notes.txt",
            "locales/en.ftl",
            "locales/en/names.txt",
        ] {
            let (_, errors) = parse_one(path, "");
            assert_eq!(
                errors,
                [PackageError::new(path, "", Problem::UnexpectedFile)],
                "{path}"
            );
        }
    }

    #[test]
    fn text_files_are_collected_by_locale() {
        let (parsed, errors) = parse_one("locales/pt-BR/teams/names.ftl", "team-a = A\n");
        assert_eq!(errors, []);
        assert_eq!(
            parsed.texts,
            [ContentText {
                locale: "pt-BR".to_owned(),
                file: "locales/pt-BR/teams/names.ftl".to_owned(),
                source: "team-a = A\n".to_owned(),
            }]
        );
    }

    #[test]
    fn text_files_must_be_utf8() {
        let mut files = PackageFiles::new();
        files.insert("locales/en/a.ftl", vec![0xff, 0xfe]);
        let mut errors = Vec::new();
        parse(&files, &mut errors);
        assert_eq!(errors[0].problem, Problem::NotUtf8);
    }

    #[test]
    fn every_folder_is_read_into_its_own_list() {
        let mut files = PackageFiles::new();
        let entities = [
            (
                "competitions",
                r#"{"id": "competition:a", "region": "region:a", "teams": []}"#,
            ),
            (
                "name-pools",
                r#"{"id": "name_pool:a", "nationality": "nationality:a", "given": [], "family": []}"#,
            ),
            (
                "nationalities",
                r#"{"id": "nationality:a", "code": "AA", "name_order": "given_first"}"#,
            ),
            ("nicknames", r#"{"id": "nickname_pool:a", "nicknames": []}"#),
            (
                "players",
                r#"{"id": "player:a", "team": "team:a", "role": "role:a"}"#,
            ),
            (
                "regions",
                r#"{"id": "region:a", "level": 0, "nationalities": {}}"#,
            ),
            ("roles", r#"{"id": "role_set:a", "roles": [], "subs": 0}"#),
            ("teams", TEAM),
        ];
        for (folder, entity) in entities {
            files.insert(format!("{folder}/a.json"), entity);
        }
        files.insert(MANIFEST, r#"{"id": "a", "version": "1.0.0", "title": "A", "license": "MIT", "authors": [], "genre": "moba", "locales": ["en"]}"#);
        files.insert(WORLD, r#"{"start_date": "2027-01-01"}"#);
        let mut errors = Vec::new();
        let parsed = parse(&files, &mut errors);
        assert_eq!(errors, []);
        assert!(parsed.manifest.is_some() && parsed.world.is_some());
        let counts = [
            parsed.competitions.len(),
            parsed.name_pools.len(),
            parsed.nationalities.len(),
            parsed.nicknames.len(),
            parsed.players.len(),
            parsed.regions.len(),
            parsed.role_sets.len(),
            parsed.teams.len(),
        ];
        assert_eq!(counts, [1; 8]);
    }

    #[test]
    fn paths_join_fields_and_indexes() {
        assert_eq!(join("", "reputation"), "reputation");
        assert_eq!(join("[2]", "reputation"), "[2].reputation");
        assert_eq!(join("[2]", "[0]"), "[2][0]");
        assert_eq!(join("[2]", ""), "[2]");
        assert_eq!(join("", ""), "");
    }
}
