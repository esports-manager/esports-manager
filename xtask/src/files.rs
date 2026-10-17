// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Small filesystem helpers shared by the checks.

use std::path::{Path, PathBuf};

use anyhow::{Context, Result};

const SKIPPED_DIRS: [&str; 4] = ["target", "node_modules", "dist", ".git"];

/// Every file under `dir` whose extension is in `extensions`, sorted.
/// A missing `dir` yields no files.
pub fn walk(dir: &Path, extensions: &[&str]) -> Result<Vec<PathBuf>> {
    let mut found = Vec::new();
    if dir.is_dir() {
        collect(dir, extensions, &mut found)?;
    }
    found.sort();
    Ok(found)
}

fn collect(dir: &Path, extensions: &[&str], found: &mut Vec<PathBuf>) -> Result<()> {
    let entries = std::fs::read_dir(dir).with_context(|| format!("listing {}", dir.display()))?;
    for entry in entries {
        let path = entry?.path();
        let name = path
            .file_name()
            .and_then(|name| name.to_str())
            .unwrap_or("");
        if path.is_dir() {
            if !SKIPPED_DIRS.contains(&name) {
                collect(&path, extensions, found)?;
            }
        } else if path
            .extension()
            .and_then(|ext| ext.to_str())
            .is_some_and(|ext| extensions.contains(&ext))
        {
            found.push(path);
        }
    }
    Ok(())
}

pub fn read(path: &Path) -> Result<String> {
    std::fs::read_to_string(path).with_context(|| format!("reading {}", path.display()))
}

/// `path` relative to `root`, for messages.
pub fn display(root: &Path, path: &Path) -> String {
    path.strip_prefix(root)
        .unwrap_or(path)
        .display()
        .to_string()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn walk_finds_matching_files_and_skips_build_dirs() {
        let root = Path::new(env!("CARGO_MANIFEST_DIR"));
        let files = walk(root, &["rs"]).unwrap();
        assert!(files.contains(&root.join("src/main.rs")));
        assert!(
            files
                .iter()
                .all(|file| file.extension().is_some_and(|ext| ext == "rs"))
        );
        assert!(files.windows(2).all(|pair| pair[0] <= pair[1]));
    }

    #[test]
    fn walk_of_a_missing_dir_is_empty() {
        let files = walk(Path::new("/definitely/not/here"), &["rs"]).unwrap();
        assert_eq!(files, Vec::<std::path::PathBuf>::new());
    }

    #[test]
    fn display_is_relative_to_root() {
        assert_eq!(
            display(Path::new("/repo"), Path::new("/repo/a/b.rs")),
            "a/b.rs"
        );
    }
}
