// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! The browser E2E tests answer with views the real backend produced:
//! `src/test/fixtures/*.json`, made by this CLI from the core package: Ana's
//! Azure Tigers from seed 42, and Bia's Onça Gaming from seed 7. This test fails when a view changes and the fixtures don't. Set
//! `UPDATE_FIXTURES=1` to rewrite them (`just e2e-fixtures`).
#![allow(clippy::unwrap_used, reason = "integration test helpers")]

use std::path::{Path, PathBuf};
use std::process::Command;

fn root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../..")
}

fn esm(data: &Path, args: &[&str]) -> serde_json::Value {
    let output = Command::new(env!("CARGO_BIN_EXE_esm"))
        .arg("--data-dir")
        .arg(data)
        .arg("--content")
        .arg(root().join("content/core"))
        .arg("--json")
        .args(args)
        .output()
        .unwrap();
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    serde_json::from_slice(&output.stdout).unwrap()
}

#[test]
fn e2e_fixtures_are_up_to_date() {
    let data = std::env::temp_dir().join(format!("esm-e2e-fixtures-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&data);
    let options = esm(&data, &["teams"]);
    for (manager, team, save, seed) in [
        ("Bia", "team:onca_gaming", "Bia's Onça", "7"),
        ("Ana", "team:azure_tigers", "Ana's Tigers", "42"),
    ] {
        esm(
            &data,
            &[
                "new-game",
                "--manager",
                manager,
                "--team",
                team,
                "--save",
                save,
                "--seed",
                seed,
            ],
        );
    }
    let roster = esm(&data, &["roster", "--save", "Ana's Tigers"]);
    let other_roster = esm(&data, &["roster", "--save", "Bia's Onça"]);
    let player = esm(
        &data,
        &["player", "--save", "Ana's Tigers", "player:kairos"],
    );
    let mut saves = esm(&data, &["saves"]);
    // Real time differs on every run; the fixture keeps fixed moments, in
    // the order the saves are listed (most recently played first).
    for (index, save) in saves.as_array_mut().unwrap().iter_mut().enumerate() {
        save["lastPlayedAt"] = serde_json::json!(1_792_000_000 - 3_600 * index);
    }

    let fixtures = root().join("src/test/fixtures");
    let mut stale = Vec::new();
    for (name, value) in [
        ("new-game-options.json", options),
        ("roster.json", roster),
        ("roster-onca.json", other_roster),
        ("player.json", player),
        ("saves.json", saves),
    ] {
        let path = fixtures.join(name);
        let text = format!("{}\n", serde_json::to_string_pretty(&value).unwrap());
        if std::env::var_os("UPDATE_FIXTURES").is_some() {
            std::fs::write(&path, &text).unwrap();
        }
        if std::fs::read_to_string(&path).unwrap_or_default() != text {
            stale.push(name);
        }
    }
    assert!(
        stale.is_empty(),
        "src/test/fixtures is out of date ({stale:?}); run `just e2e-fixtures`"
    );
}
