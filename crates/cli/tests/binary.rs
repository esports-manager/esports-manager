// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

use std::process::Command;

#[test]
fn binary_prints_its_version() {
    let output = Command::new(env!("CARGO_BIN_EXE_esm"))
        .arg("--version")
        .output()
        .expect("the esm binary runs");

    assert!(output.status.success());
    assert_eq!(
        String::from_utf8_lossy(&output.stdout).trim(),
        cli::version_line()
    );
}
