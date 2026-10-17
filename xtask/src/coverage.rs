// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Per-crate line coverage gate (ADR 0008), reading a `cargo llvm-cov --json`
//! report.

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

use anyhow::{Context, Result};
use serde::Deserialize;

use crate::files;
use crate::workspace::{self, TOOLING};

#[derive(Debug, Deserialize)]
struct Report {
    data: Vec<Export>,
}

#[derive(Debug, Deserialize)]
struct Export {
    files: Vec<FileEntry>,
}

#[derive(Debug, Deserialize)]
struct FileEntry {
    filename: String,
    summary: Summary,
}

#[derive(Debug, Deserialize)]
struct Summary {
    lines: Lines,
}

#[derive(Debug, Clone, Copy, Default, Deserialize, PartialEq, Eq)]
pub struct Lines {
    pub count: u64,
    pub covered: u64,
}

pub fn run(root: &Path, thresholds: &BTreeMap<String, u32>, report: &Path) -> Result<Vec<String>> {
    let mut dirs = workspace::member_dirs(&workspace::metadata(root)?);
    dirs.retain(|name, _| !TOOLING.contains(&name.as_str()));
    let (lines, violations) = evaluate(&dirs, thresholds, &files::read(report)?)?;
    for line in lines {
        println!("{line}");
    }
    Ok(violations)
}

/// Reads an llvm-cov JSON report and checks it against the thresholds.
fn evaluate(
    dirs: &BTreeMap<String, PathBuf>,
    thresholds: &BTreeMap<String, u32>,
    report: &str,
) -> Result<(Vec<String>, Vec<String>)> {
    let report: Report =
        serde_json::from_str(report).context("parsing the llvm-cov JSON report")?;
    let entries = report
        .data
        .iter()
        .flat_map(|export| &export.files)
        .map(|file| (file.filename.as_str(), file.summary.lines));
    Ok(check(thresholds, &per_crate(dirs, entries)))
}

/// Sums line counts per workspace package. A file belongs to the package
/// whose directory is the deepest one containing it; files outside every
/// package (dependencies, tooling) are ignored.
pub fn per_crate<'a>(
    dirs: &BTreeMap<String, PathBuf>,
    files: impl IntoIterator<Item = (&'a str, Lines)>,
) -> BTreeMap<String, Lines> {
    let mut totals: BTreeMap<String, Lines> = BTreeMap::new();
    for (filename, lines) in files {
        let owner = dirs
            .iter()
            .filter(|(_, dir)| Path::new(filename).starts_with(dir))
            .max_by_key(|(_, dir)| dir.components().count());
        let Some((name, _)) = owner else {
            continue;
        };
        let total = totals.entry(name.clone()).or_default();
        total.count += lines.count;
        total.covered += lines.covered;
    }
    totals
}

/// Returns a report line per crate and the violations.
pub fn check(
    thresholds: &BTreeMap<String, u32>,
    totals: &BTreeMap<String, Lines>,
) -> (Vec<String>, Vec<String>) {
    let mut report = Vec::new();
    let mut violations = Vec::new();

    for (name, &minimum) in thresholds {
        let lines = totals.get(name).copied().unwrap_or_default();
        if lines.count == 0 {
            report.push(format!("{name}: no code yet (minimum {minimum}%)"));
            continue;
        }
        let percent = lines.covered * 100 / lines.count;
        report.push(format!(
            "{name}: {percent}% of {} lines (minimum {minimum}%)",
            lines.count
        ));
        if lines.covered * 100 < u64::from(minimum) * lines.count {
            violations.push(format!(
                "crate `{name}` has {percent}% line coverage, below its {minimum}% minimum"
            ));
        }
    }
    for name in totals.keys() {
        if !thresholds.contains_key(name) {
            violations.push(format!(
                "crate `{name}` has no coverage minimum in quality.toml [coverage]"
            ));
        }
    }

    (report, violations)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn lines(count: u64, covered: u64) -> Lines {
        Lines { count, covered }
    }

    fn dirs() -> BTreeMap<String, PathBuf> {
        BTreeMap::from([
            ("app".to_owned(), PathBuf::from("/repo/crates/app")),
            ("domain".to_owned(), PathBuf::from("/repo/crates/domain")),
            (
                "esports-manager".to_owned(),
                PathBuf::from("/repo/src-tauri"),
            ),
        ])
    }

    #[test]
    fn sums_files_per_package_and_ignores_files_elsewhere() {
        let totals = per_crate(
            &dirs(),
            [
                ("/repo/crates/domain/src/a.rs", lines(10, 9)),
                ("/repo/crates/domain/src/b.rs", lines(10, 10)),
                ("/repo/crates/app/src/lib.rs", lines(4, 1)),
                ("/repo/src-tauri/src/lib.rs", lines(8, 6)),
                ("/repo/xtask/src/main.rs", lines(50, 0)),
                ("/home/user/.cargo/registry/x.rs", lines(5, 0)),
            ],
        );
        assert_eq!(
            totals,
            BTreeMap::from([
                ("app".to_owned(), lines(4, 1)),
                ("domain".to_owned(), lines(20, 19)),
                ("esports-manager".to_owned(), lines(8, 6)),
            ])
        );
    }

    #[test]
    fn a_file_belongs_to_the_deepest_package_containing_it() {
        let dirs = BTreeMap::from([
            ("outer".to_owned(), PathBuf::from("/repo/a")),
            ("inner".to_owned(), PathBuf::from("/repo/a/b")),
        ]);
        let totals = per_crate(&dirs, [("/repo/a/b/src/lib.rs", lines(1, 1))]);
        assert_eq!(totals, BTreeMap::from([("inner".to_owned(), lines(1, 1))]));
    }

    #[test]
    fn sibling_directories_sharing_a_prefix_are_not_confused() {
        let dirs = BTreeMap::from([("app".to_owned(), PathBuf::from("/repo/crates/app"))]);
        let totals = per_crate(
            &dirs,
            [("/repo/crates/application/src/lib.rs", lines(1, 1))],
        );
        assert_eq!(totals, BTreeMap::new());
    }

    #[test]
    fn coverage_at_the_minimum_passes() {
        let thresholds = BTreeMap::from([("domain".to_owned(), 90)]);
        let totals = BTreeMap::from([("domain".to_owned(), lines(10, 9))]);
        let (report, violations) = check(&thresholds, &totals);
        assert_eq!(report, ["domain: 90% of 10 lines (minimum 90%)"]);
        assert_eq!(violations, Vec::<String>::new());
    }

    #[test]
    fn coverage_below_the_minimum_fails_even_by_a_fraction() {
        let thresholds = BTreeMap::from([("domain".to_owned(), 90)]);
        let totals = BTreeMap::from([("domain".to_owned(), lines(1000, 899))]);
        let (_, violations) = check(&thresholds, &totals);
        assert_eq!(
            violations,
            ["crate `domain` has 89% line coverage, below its 90% minimum"]
        );
    }

    #[test]
    fn crates_without_code_are_skipped() {
        let thresholds = BTreeMap::from([("db".to_owned(), 80)]);
        let (report, violations) = check(&thresholds, &BTreeMap::new());
        assert_eq!(report, ["db: no code yet (minimum 80%)"]);
        assert_eq!(violations, Vec::<String>::new());
    }

    #[test]
    fn crates_without_a_minimum_fail() {
        let totals = BTreeMap::from([("rogue".to_owned(), lines(1, 1))]);
        let (_, violations) = check(&BTreeMap::new(), &totals);
        assert_eq!(
            violations,
            ["crate `rogue` has no coverage minimum in quality.toml [coverage]"]
        );
    }

    #[test]
    fn evaluates_an_llvm_cov_report() {
        let report = r#"{"data":[{"files":[
            {"filename":"/repo/crates/domain/src/lib.rs","summary":{"lines":{"count":10,"covered":5,"percent":50.0}}}
        ]}]}"#;
        let thresholds = BTreeMap::from([("domain".to_owned(), 90)]);

        let (_, violations) = evaluate(&dirs(), &thresholds, report).unwrap();

        assert_eq!(
            violations,
            ["crate `domain` has 50% line coverage, below its 90% minimum"]
        );
    }

    #[test]
    fn a_malformed_report_is_an_error() {
        assert!(evaluate(&dirs(), &BTreeMap::new(), "{}").is_err());
    }
}
