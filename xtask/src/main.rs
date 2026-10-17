// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Repository checks that no off-the-shelf tool covers (ADR 0008).
//!
//! Each check prints its violations and exits non-zero if there are any.
//! Run them through `just check`, or one at a time with `cargo xtask <check>`.

mod arch;
mod config;
mod coverage;
mod files;
mod rest;
mod trace;
mod vocab;
mod workspace;

use std::path::{Path, PathBuf};
use std::process::ExitCode;

use anyhow::{Context, Result, bail};

const USAGE: &str =
    "usage: cargo xtask <arch | vocab | trace | rest-patterns | coverage <llvm-cov.json>>";

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().skip(1).collect();
    match run(&args) {
        Ok(violations) if violations.is_empty() => ExitCode::SUCCESS,
        Ok(violations) => {
            for violation in &violations {
                eprintln!("error: {violation}");
            }
            eprintln!("{} violation(s)", violations.len());
            ExitCode::FAILURE
        }
        Err(error) => {
            eprintln!("error: {error:#}");
            ExitCode::FAILURE
        }
    }
}

fn run(args: &[String]) -> Result<Vec<String>> {
    let root = workspace_root()?;
    let quality = config::Quality::load(&root.join("quality.toml"))?;
    match args {
        [check] if check == "arch" => arch::run(&root, &quality.architecture),
        [check] if check == "vocab" => vocab::run(&root, &quality.vocabulary),
        [check] if check == "trace" => trace::run(&root),
        [check] if check == "rest-patterns" => rest::run(&root, &quality.packages.conversion),
        [check, report] if check == "coverage" => {
            coverage::run(&root, &quality.coverage, Path::new(report))
        }
        _ => bail!(USAGE),
    }
}

fn workspace_root() -> Result<PathBuf> {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .map(Path::to_path_buf)
        .context("xtask must live one level below the workspace root")
}
