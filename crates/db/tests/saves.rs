// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! The save store against real files (saves spec).
#![allow(clippy::unwrap_used, reason = "integration test helpers")]

mod support;

use app::saves::{Damage, OpenSave, SaveError, SaveStore, Timestamp};
use db::SqliteSaveStore;
use support::{files, folder, id, meta, new_save, texts, world};

#[test]
fn a_new_save_is_one_file_with_its_metadata() {
    // spec: SAVE-008
    // Given
    let dir = folder("new");
    let store = SqliteSaveStore::new(dir.clone());
    let (meta, world, texts) = (meta("Ana's Tigers", 100), world(42), texts());
    // When
    let file = store.create(new_save(&meta, &world, &texts)).unwrap();
    // Then
    assert_eq!(file, "ana-s-tigers.esmsave");
    assert_eq!(files(&dir), ["ana-s-tigers.esmsave"]);
    let open = store.open(&file, Timestamp(100)).unwrap();
    assert_eq!(open.meta(), &meta);
    drop(open);
    // The schema version is the file's record of applied migrations: every
    // one the game has.
    let migrations = std::fs::read_dir(concat!(env!("CARGO_MANIFEST_DIR"), "/migrations"))
        .unwrap()
        .count();
    assert_eq!(
        raw_count(&dir.join(&file), "__diesel_schema_migrations"),
        migrations
    );
}

#[test]
fn a_failed_creation_leaves_nothing_behind() {
    // spec: SAVE-009
    // Given a world that breaks a constraint half-way through being written
    let dir = folder("failed");
    let store = SqliteSaveStore::new(dir.clone());
    let mut world = world(42);
    let duplicate = world.players[0].clone();
    world.players.push(duplicate);
    let (meta, texts) = (meta("Tigers", 100), texts());
    // When
    let result = store.create(new_save(&meta, &world, &texts));
    // Then
    assert!(matches!(result, Err(SaveError::Storage(_))));
    assert_eq!(files(&dir), Vec::<String>::new());
}

#[test]
fn save_names_are_unique_ignoring_case() {
    // spec: SAVE-010
    // Given
    let dir = folder("unique");
    let store = SqliteSaveStore::new(dir.clone());
    let (world, texts) = (world(42), texts());
    store
        .create(new_save(&meta("Tigers", 100), &world, &texts))
        .unwrap();
    let before = std::fs::read(dir.join("tigers.esmsave")).unwrap();
    // When
    let result = store.create(new_save(&meta("tigers", 200), &world, &texts));
    // Then
    assert_eq!(result, Err(SaveError::NameTaken("tigers".to_owned())));
    assert_eq!(std::fs::read(dir.join("tigers.esmsave")).unwrap(), before);
    assert_eq!(files(&dir), ["tigers.esmsave"]);
}

#[test]
fn different_names_with_the_same_slug_get_distinct_files() {
    // spec: SAVE-011
    // Given
    let dir = folder("slug");
    let store = SqliteSaveStore::new(dir);
    let (world, texts) = (world(42), texts());
    store
        .create(new_save(&meta("Tigers!", 100), &world, &texts))
        .unwrap();
    // When
    let file = store
        .create(new_save(&meta("Tigers?", 100), &world, &texts))
        .unwrap();
    // Then
    assert_eq!(file, "tigers-2.esmsave");
}

#[test]
fn the_list_comes_from_the_folder_newest_first() {
    // spec: SAVE-012
    // Given
    let dir = folder("list");
    let elsewhere = folder("list-elsewhere");
    let (world, texts) = (world(42), texts());
    let store = SqliteSaveStore::new(dir.clone());
    store
        .create(new_save(&meta("Older", 100), &world, &texts))
        .unwrap();
    store
        .create(new_save(&meta("Newer", 300), &world, &texts))
        .unwrap();
    SqliteSaveStore::new(elsewhere.clone())
        .create(new_save(&meta("Copied", 200), &world, &texts))
        .unwrap();
    std::fs::copy(elsewhere.join("copied.esmsave"), dir.join("copied.esmsave")).unwrap();
    // When
    let listings = store.list().unwrap();
    // Then
    let names: Vec<String> = listings.into_iter().map(|l| l.save.unwrap().name).collect();
    assert_eq!(names, ["Newer", "Copied", "Older"]);
}

#[test]
fn a_damaged_file_does_not_break_the_list() {
    // spec: SAVE-013
    // Given
    let dir = folder("damaged");
    let store = SqliteSaveStore::new(dir.clone());
    let (world, texts) = (world(42), texts());
    store
        .create(new_save(&meta("Valid", 100), &world, &texts))
        .unwrap();
    std::fs::write(
        dir.join("broken.esmsave"),
        b"not a database at all, just some text that is long enough",
    )
    .unwrap();
    // When
    let listings = store.list().unwrap();
    // Then
    assert_eq!(listings.len(), 2);
    assert_eq!(listings[0].save.as_ref().unwrap().name, "Valid");
    assert_eq!(
        (listings[1].file.as_str(), &listings[1].save),
        ("broken.esmsave", &Err(Damage::NotASave))
    );
}

#[test]
fn an_empty_or_foreign_database_is_not_a_save() {
    let dir = folder("foreign");
    std::fs::write(dir.join("empty.esmsave"), b"").unwrap();
    let store = SqliteSaveStore::new(dir);
    let listings = store.list().unwrap();
    assert_eq!(listings[0].save, Err(Damage::NotASave));
    assert_eq!(
        store.open("empty.esmsave", Timestamp(1)).map(|_| ()),
        Err(SaveError::NotASave)
    );
}

#[test]
fn newer_saves_are_refused() {
    // spec: SAVE-014
    // Given
    let dir = folder("newer");
    let store = SqliteSaveStore::new(dir.clone());
    let (world, texts) = (world(42), texts());
    let file = store
        .create(new_save(&meta("Future", 100), &world, &texts))
        .unwrap();
    raw_execute(
        &dir.join(&file),
        "INSERT INTO __diesel_schema_migrations (version) VALUES ('99990101000000')",
    );
    let before = std::fs::read(dir.join(&file)).unwrap();
    // When
    let result = store.open(&file, Timestamp(200));
    // Then
    assert_eq!(result.map(|_| ()), Err(SaveError::NewerVersion));
    assert_eq!(std::fs::read(dir.join(&file)).unwrap(), before);
    assert_eq!(store.list().unwrap()[0].save, Err(Damage::NewerVersion));
}

#[test]
fn a_save_round_trips() {
    // spec: SAVE-015
    // Given
    let dir = folder("round-trip");
    let store = SqliteSaveStore::new(dir);
    let (meta, world, texts) = (meta("Round trip", 100), world(42), texts());
    let file = store.create(new_save(&meta, &world, &texts)).unwrap();
    // When
    let mut open = store.open(&file, Timestamp(100)).unwrap();
    // Then
    let mut players = Vec::new();
    for team in &world.teams {
        assert_eq!(open.team(&team.id).unwrap().as_ref(), Some(team));
        players.extend(open.players_of(&team.id).unwrap());
    }
    assert_eq!(players, world.players);
    assert_eq!(open.roles().unwrap(), world.roles);
    assert_eq!(open.regions().unwrap(), world.regions);
    assert_eq!(open.nationalities().unwrap(), world.nationalities);
    assert_eq!(open.competitions().unwrap(), world.competitions);
    assert_eq!(open.texts().unwrap(), texts);
    assert_eq!(
        open.player(&world.players[3].id).unwrap().as_ref(),
        Some(&world.players[3])
    );
    assert_eq!(open.player(&id("player:nobody")).unwrap(), None);
    assert_eq!(open.team(&id("team:nobody")).unwrap(), None);
}

#[test]
fn generated_ids_survive_closing_and_reopening() {
    // spec: GEN-018
    // Given
    let dir = folder("ids");
    let store = SqliteSaveStore::new(dir);
    let (meta, world, texts) = (meta("Ids", 100), world(42), texts());
    let file = store.create(new_save(&meta, &world, &texts)).unwrap();
    // When
    let mut reopened = store.open(&file, Timestamp(100)).unwrap();
    // Then
    let ids: Vec<String> = reopened
        .players_of(&id("team:a"))
        .unwrap()
        .iter()
        .map(|p| p.id.to_string())
        .collect();
    assert_eq!(ids[0], "player:kairos");
    assert_eq!(
        &ids[1..],
        [
            "player:a.1",
            "player:a.2",
            "player:a.3",
            "player:a.4",
            "player:a.5",
            "player:a.6"
        ]
    );
}

#[test]
fn opening_updates_last_played() {
    // spec: SAVE-016
    // Given
    let dir = folder("last-played");
    let store = SqliteSaveStore::new(dir);
    let (world, texts) = (world(42), texts());
    let file = store
        .create(new_save(&meta("Played", 36_000), &world, &texts))
        .unwrap();
    // When
    let open = store.open(&file, Timestamp(43_200)).unwrap();
    // Then
    assert_eq!(open.meta().last_played_at, Timestamp(43_200));
    assert_eq!(open.meta().created_at, Timestamp(36_000));
    drop(open);
    assert_eq!(
        store.list().unwrap()[0]
            .save
            .as_ref()
            .unwrap()
            .last_played_at,
        Timestamp(43_200)
    );
}

#[test]
fn a_name_with_no_ascii_letters_still_gets_a_file() {
    // spec: SAVE-017
    // Given
    let dir = folder("unicode");
    let store = SqliteSaveStore::new(dir);
    let (meta, world, texts) = (meta("호랑이", 100), world(42), texts());
    // When
    let file = store.create(new_save(&meta, &world, &texts)).unwrap();
    // Then
    assert_eq!(file, "save.esmsave");
    assert_eq!(
        store.list().unwrap()[0].save.as_ref().unwrap().name,
        "호랑이"
    );
}

#[test]
fn leftovers_of_a_crash_are_cleaned_up() {
    // spec: SAVE-019
    // Given
    let dir = folder("leftovers");
    // A half-written SQLite file with its rollback journal, and a journal
    // whose temporary save is already gone.
    let mut half = b"SQLite format 3\0".to_vec();
    half.resize(4096, 0);
    std::fs::write(dir.join("tigers.1234-0.tmp"), &half).unwrap();
    std::fs::write(dir.join("tigers.1234-0.tmp-journal"), [0_u8; 512]).unwrap();
    std::fs::write(dir.join("lions.99-3.tmp-journal"), [0_u8; 512]).unwrap();
    // When
    let store = SqliteSaveStore::new(dir.clone());
    // Then
    assert_eq!(files(&dir), Vec::<String>::new());
    let (world, texts) = (world(42), texts());
    assert_eq!(
        store
            .create(new_save(&meta("Tigers", 100), &world, &texts))
            .unwrap(),
        "tigers.esmsave"
    );
}

#[test]
fn creation_takes_a_free_file_and_leaves_other_files_alone() {
    // SAVE-018 at the store's level: a file already under the name, even one
    // that isn't a save, is never a target.
    let dir = folder("existing-file");
    std::fs::write(dir.join("tigers.esmsave"), b"existing").unwrap();
    let store = SqliteSaveStore::new(dir.clone());
    let (world, texts) = (world(42), texts());
    let file = store
        .create(new_save(&meta("Tigers", 100), &world, &texts))
        .unwrap();
    assert_eq!(file, "tigers-2.esmsave");
    assert_eq!(
        std::fs::read(dir.join("tigers.esmsave")).unwrap(),
        b"existing"
    );
}

#[test]
fn two_creations_at_once_never_share_a_name() {
    // spec: SAVE-010
    // Given two creations of "Tigers" racing in one folder, many times over
    for round in 0..10 {
        let dir = folder(&format!("race-{round}"));
        let (world, texts) = (world(42), texts());
        // When both run at once
        let results: Vec<Result<String, SaveError>> = std::thread::scope(|scope| {
            let racers: Vec<_> = (0..2)
                .map(|_| {
                    let (dir, world, texts) = (&dir, &world, &texts);
                    scope.spawn(move || {
                        SqliteSaveStore::new(dir.clone()).create(new_save(
                            &meta("Tigers", 100),
                            world,
                            texts,
                        ))
                    })
                })
                .collect();
            racers
                .into_iter()
                .map(|racer| racer.join().unwrap())
                .collect()
        });
        // Then exactly one has the name; the other is told it's taken
        let created: Vec<&String> = results.iter().filter_map(|r| r.as_ref().ok()).collect();
        assert_eq!(created, [&"tigers.esmsave".to_owned()], "{results:?}");
        assert!(results.contains(&Err(SaveError::NameTaken("Tigers".to_owned()))));
    }
}

#[test]
fn an_open_save_cannot_be_opened_twice() {
    // spec: SAVE-020
    // Given
    let dir = folder("in-use");
    let store = SqliteSaveStore::new(dir);
    let (world, texts) = (world(42), texts());
    let file = store
        .create(new_save(&meta("Busy", 100), &world, &texts))
        .unwrap();
    let held = store.open(&file, Timestamp(200)).unwrap();
    // When
    let second = store.open(&file, Timestamp(300));
    // Then
    assert_eq!(second.map(|_| ()), Err(SaveError::InUse));
    // Its metadata is still listed, marked in use.
    let listing = &store.list().unwrap()[0];
    assert!(listing.in_use);
    assert_eq!(listing.save.as_ref().unwrap().name, "Busy");
    drop(held);
    assert!(!store.list().unwrap()[0].in_use);
    assert!(store.open(&file, Timestamp(400)).is_ok());
}

#[test]
fn a_name_is_taken_even_by_a_save_that_is_open() {
    let dir = folder("taken-open");
    let store = SqliteSaveStore::new(dir);
    let (world, texts) = (world(42), texts());
    let file = store
        .create(new_save(&meta("Tigers", 100), &world, &texts))
        .unwrap();
    let _held = store.open(&file, Timestamp(200)).unwrap();
    assert_eq!(
        store.create(new_save(&meta("tigers", 300), &world, &texts)),
        Err(SaveError::NameTaken("tigers".to_owned()))
    );
}

#[test]
fn a_name_is_taken_even_by_a_save_from_a_newer_version() {
    let dir = folder("taken-newer");
    let store = SqliteSaveStore::new(dir.clone());
    let (world, texts) = (world(42), texts());
    let file = store
        .create(new_save(&meta("Future", 100), &world, &texts))
        .unwrap();
    raw_execute(
        &dir.join(&file),
        "INSERT INTO __diesel_schema_migrations (version) VALUES ('99990101000000')",
    );
    assert_eq!(
        store.create(new_save(&meta("FUTURE", 300), &world, &texts)),
        Err(SaveError::NameTaken("FUTURE".to_owned()))
    );
}

#[test]
fn an_open_save_keeps_its_place_in_the_list() {
    let dir = folder("open-order");
    let store = SqliteSaveStore::new(dir.clone());
    let (world, texts) = (world(42), texts());
    store
        .create(new_save(&meta("Alpha", 100), &world, &texts))
        .unwrap();
    let zeta = store
        .create(new_save(&meta("Zeta", 50), &world, &texts))
        .unwrap();
    std::fs::write(dir.join("broken.esmsave"), b"not a save").unwrap();
    let _held = store.open(&zeta, Timestamp(500)).unwrap();
    let files: Vec<String> = store.list().unwrap().into_iter().map(|l| l.file).collect();
    assert_eq!(files, ["zeta.esmsave", "alpha.esmsave", "broken.esmsave"]);
}

#[test]
fn saves_played_at_the_same_moment_have_a_stable_order() {
    // spec: SAVE-021
    // Given
    let dir = folder("ties");
    let store = SqliteSaveStore::new(dir.clone());
    let (world, texts) = (world(42), texts());
    store
        .create(new_save(&meta("Beta", 100), &world, &texts))
        .unwrap();
    store
        .create(new_save(&meta("alpha", 100), &world, &texts))
        .unwrap();
    // A hand-made copy has the same name and moment; its file breaks the tie.
    std::fs::copy(dir.join("alpha.esmsave"), dir.join("alpha-copy.esmsave")).unwrap();
    // When
    let listed = || {
        store
            .list()
            .unwrap()
            .into_iter()
            .map(|l| (l.save.unwrap().name, l.file))
            .collect::<Vec<_>>()
    };
    // Then names sort as a person reads them, ignoring case
    let expected = [
        ("alpha".to_owned(), "alpha-copy.esmsave".to_owned()),
        ("alpha".to_owned(), "alpha.esmsave".to_owned()),
        ("Beta".to_owned(), "beta.esmsave".to_owned()),
    ];
    assert_eq!(listed(), expected);
    assert_eq!(listed(), expected);
}

#[test]
fn only_save_files_in_the_folder_can_be_opened() {
    let dir = folder("not-found");
    let store = SqliteSaveStore::new(dir);
    for file in ["missing.esmsave", "../escape.esmsave", "notes.txt"] {
        assert_eq!(
            store.open(file, Timestamp(1)).map(|_| ()),
            Err(SaveError::NotFound(file.to_owned()))
        );
    }
}

#[test]
fn saves_outside_the_folder_cannot_be_opened() {
    let dir = folder("escape");
    let (world, texts) = (world(42), texts());
    SqliteSaveStore::new(dir.clone())
        .create(new_save(&meta("Outside", 100), &world, &texts))
        .unwrap();
    std::fs::create_dir_all(dir.join("inner")).unwrap();
    let store = SqliteSaveStore::new(dir.join("inner"));
    assert_eq!(
        store.open("../outside.esmsave", Timestamp(1)).map(|_| ()),
        Err(SaveError::NotFound("../outside.esmsave".to_owned()))
    );
}

#[test]
fn a_missing_folder_cannot_be_listed() {
    let store = SqliteSaveStore::new(std::env::temp_dir().join("esm-db-definitely-missing"));
    assert!(matches!(store.list(), Err(SaveError::Storage(_))));
}

/// The number of rows in `table`, read as a tool outside the game would.
fn raw_count(path: &std::path::Path, table: &str) -> usize {
    use diesel::{Connection, QueryableByName, RunQueryDsl, sqlite::SqliteConnection};
    #[derive(QueryableByName)]
    struct Count {
        #[diesel(sql_type = diesel::sql_types::BigInt)]
        rows: i64,
    }
    let mut connection = SqliteConnection::establish(path.to_str().unwrap()).unwrap();
    let count: Count = diesel::sql_query(format!("SELECT COUNT(*) AS rows FROM {table}"))
        .get_result(&mut connection)
        .unwrap();
    usize::try_from(count.rows).unwrap()
}

/// Runs raw SQL on a save, as a tool outside the game would.
fn raw_execute(path: &std::path::Path, sql: &str) {
    use diesel::{Connection, RunQueryDsl, sqlite::SqliteConnection};
    let mut connection = SqliteConnection::establish(path.to_str().unwrap()).unwrap();
    diesel::sql_query(sql).execute(&mut connection).unwrap();
}
