// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! A small generated world and a scratch saves folder for the store tests.
#![allow(
    clippy::unwrap_used,
    clippy::expect_used,
    reason = "test support, which may panic"
)]
#![allow(dead_code, reason = "each test file uses part of the support")]

use std::path::PathBuf;

use app::content::ContentText;
use app::saves::{NewSave, PackageRecord, SaveMeta, Timestamp};
use domain::rng::WorldSeed;
use esports::Genre;
use esports::moba::world::World;

pub use esports::moba::fixtures::{id, world};

pub fn meta(name: &str, last_played: i64) -> SaveMeta {
    SaveMeta {
        name: name.to_owned(),
        manager_name: "Ana".to_owned(),
        team: id("team:a"),
        genre: Genre::Moba,
        seed: WorldSeed::new(42),
        game_version: "0.0.0".to_owned(),
        game_date: "2027-01-01".parse().unwrap(),
        created_at: Timestamp(last_played),
        last_played_at: Timestamp(last_played),
        packages: vec![PackageRecord {
            id: "core".to_owned(),
            version: "0.1.0".to_owned(),
            content_hash: [7; 32],
        }],
    }
}

pub fn texts() -> Vec<ContentText> {
    vec![
        ContentText {
            locale: "en".into(),
            file: "locales/en/teams.ftl".into(),
            source: "team-a = A\n".into(),
        },
        ContentText {
            locale: "pt-BR".into(),
            file: "locales/pt-BR/teams.ftl".into(),
            source: "team-a = A\n".into(),
        },
    ]
}

/// A copy of the parts, so a test can write the same world twice.
pub fn new_save(meta: &SaveMeta, world: &World, texts: &[ContentText]) -> NewSave {
    NewSave {
        meta: meta.clone(),
        world: world.clone(),
        texts: texts.to_vec(),
    }
}

/// An empty folder unique to one test.
pub fn folder(name: &str) -> PathBuf {
    let dir = std::env::temp_dir().join(format!("esm-db-{name}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&dir);
    std::fs::create_dir_all(&dir).unwrap();
    dir
}

pub fn files(dir: &std::path::Path) -> Vec<String> {
    let mut names: Vec<String> = std::fs::read_dir(dir)
        .unwrap()
        .map(|entry| entry.unwrap().file_name().into_string().unwrap())
        // The folder's creation lock stays once a save was ever created.
        .filter(|name| name != ".create.lock")
        .collect();
    names.sort();
    names
}
