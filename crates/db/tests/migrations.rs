// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Every schema version keeps a fixture save, and every later version must
//! open it (ADR 0004). The fixture for a version is written once, when its
//! migration lands, and never regenerated: `UPDATE_FIXTURES=1` only writes
//! fixtures that don't exist yet.
#![allow(clippy::unwrap_used, reason = "integration test helpers")]

mod support;

use std::path::Path;

use app::saves::{OpenSave, SaveStore, Timestamp};
use db::SqliteSaveStore;
use support::{folder, id, meta, new_save, texts, world};

const FIRST: &str = "2026-10-16-000000_create_world.esmsave";

fn fixture(name: &str) -> std::path::PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("tests/fixtures")
        .join(name)
}

#[test]
fn the_first_schema_version_still_opens() {
    let path = fixture(FIRST);
    if std::env::var_os("UPDATE_FIXTURES").is_some() && !path.exists() {
        let dir = folder("fixture-source");
        let (meta, world, texts) = (meta("Fixture", 1_000), world(42), texts());
        let file = SqliteSaveStore::new(dir.clone())
            .create(new_save(&meta, &world, &texts))
            .unwrap();
        std::fs::copy(dir.join(file), &path).unwrap();
    }

    let dir = folder("fixture-open");
    std::fs::copy(&path, dir.join("fixture.esmsave")).unwrap();
    // Listing never migrates, so it must read a save of any older version.
    let store = SqliteSaveStore::new(dir.clone());
    let listed = store.list().unwrap();
    assert_eq!(listed[0].save.as_ref().unwrap().name, "Fixture");
    let mut open = SqliteSaveStore::new(dir)
        .open("fixture.esmsave", Timestamp(2_000))
        .unwrap();

    assert_eq!(open.meta().name, "Fixture");
    assert_eq!(open.meta().created_at, Timestamp(1_000));
    let players = open.players_of(&id("team:a")).unwrap();
    assert_eq!(players.len(), 7);
    assert_eq!(players[0].nickname, "Kairos");
    assert_eq!(open.roles().unwrap().roles().len(), 5);
}
