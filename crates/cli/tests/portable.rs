// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Portable mode with the real binary, not just the resolution rules: a
//! copy of `esm` with a `portable` file next to it keeps its saves beside
//! it. The cross-platform CI job runs this on Windows too. macOS ignores
//! the marker (SAVE-005), so a run there would write into the real OS data
//! folder; it is left out.
#![cfg(not(target_os = "macos"))]

use std::path::{Path, PathBuf};
use std::process::Command;

fn core() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../../content/core")
}

#[test]
fn a_portable_copy_keeps_its_saves_next_to_it() {
    // spec: SAVE-002
    // Given a copy of the binary with a `portable` file next to it
    let folder = std::env::temp_dir().join(format!("esm-portable-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&folder);
    std::fs::create_dir_all(&folder).unwrap();
    let built = Path::new(env!("CARGO_BIN_EXE_esm"));
    let copy = folder.join(built.file_name().unwrap());
    std::fs::copy(built, &copy).unwrap();
    std::fs::write(folder.join("portable"), "").unwrap();

    // When it starts a new game, with no `--data-dir`
    let output = Command::new(&copy)
        .arg("--content")
        .arg(core())
        .args([
            "new-game",
            "--manager",
            "Ana",
            "--team",
            "team:azure_tigers",
        ])
        .args(["--save", "Portable", "--seed", "1"])
        .output()
        .unwrap();

    // Then the save is in `data/saves` beside it
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    let saves: Vec<String> = std::fs::read_dir(folder.join("data").join("saves"))
        .unwrap()
        .map(|entry| entry.unwrap().file_name().into_string().unwrap())
        .filter(|name| name.ends_with(".esmsave"))
        .collect();
    assert_eq!(saves, ["portable.esmsave"]);
    let _ = std::fs::remove_dir_all(&folder);
}
