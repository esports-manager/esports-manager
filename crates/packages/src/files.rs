// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Reading a package directory into memory.
//!
//! Everything after this works on [`PackageFiles`], so the loader's rules are
//! tested without touching the filesystem.

use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};

use sha2::{Digest, Sha256};

/// A package's files, keyed by their path relative to the package root with
/// `/` separators. Iteration is in sorted path order, the order the loader
/// reads files in on every OS.
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct PackageFiles(BTreeMap<String, Vec<u8>>);

impl PackageFiles {
    #[must_use]
    pub fn new() -> Self {
        Self::default()
    }

    /// Adds or replaces a file.
    pub fn insert(&mut self, path: impl Into<String>, contents: impl Into<Vec<u8>>) {
        self.0.insert(path.into(), contents.into());
    }

    /// Reads every file under `root`.
    ///
    /// # Errors
    ///
    /// When a directory or file can't be read, or a path isn't UTF-8.
    pub fn read_dir(root: &Path) -> std::io::Result<Self> {
        let (files, unreadable) = Self::read_dir_reporting(root)?;
        match unreadable.into_iter().next() {
            Some((_, error)) => Err(error),
            None => Ok(files),
        }
    }

    /// Reads every file under `root` it can, and reports each file or folder
    /// it can't, by its path relative to the root. Symbolic links are
    /// followed, so a package can link in a folder kept elsewhere. A link to
    /// the package's own folder or one above it (`..`, `~`, `/`), or to a
    /// folder already read, is reported instead, so a link can't make the
    /// loader loop or read the whole disk.
    ///
    /// # Errors
    ///
    /// When `root` itself can't be read.
    pub fn read_dir_reporting(
        root: &Path,
    ) -> std::io::Result<(Self, Vec<(String, std::io::Error)>)> {
        let mut files = Self::new();
        let mut unreadable = Vec::new();
        let entries = std::fs::read_dir(root)?;
        let real_root = std::fs::canonicalize(root)?;
        let mut walk = Walk {
            root: real_root.clone(),
            visited: BTreeSet::from([real_root]),
            files: &mut files,
            unreadable: &mut unreadable,
        };
        walk.read(entries, root, "");
        Ok((files, unreadable))
    }

    pub fn iter(&self) -> impl Iterator<Item = (&str, &[u8])> {
        self.0
            .iter()
            .map(|(path, contents)| (path.as_str(), contents.as_slice()))
    }

    /// SHA-256 over every path and its contents, in sorted order. Two packages
    /// with the same hash hold the same files.
    #[must_use]
    pub fn content_hash(&self) -> [u8; 32] {
        let mut hasher = Sha256::new();
        for (path, contents) in &self.0 {
            hasher.update((path.len() as u64).to_le_bytes());
            hasher.update(path.as_bytes());
            hasher.update((contents.len() as u64).to_le_bytes());
            hasher.update(contents);
        }
        hasher.finalize().into()
    }
}

/// One reading of a package folder.
struct Walk<'a> {
    /// The package root, with links resolved.
    root: PathBuf,
    /// Every folder read so far, with links resolved.
    visited: BTreeSet<PathBuf>,
    files: &'a mut PackageFiles,
    unreadable: &'a mut Vec<(String, std::io::Error)>,
}

impl Walk<'_> {
    fn read(&mut self, entries: std::fs::ReadDir, dir: &Path, prefix: &str) {
        // Sorted, so problems are reported in the same order on every OS.
        let mut entries: Vec<_> = entries.collect();
        entries.sort_by_key(|entry| entry.as_ref().map(std::fs::DirEntry::file_name).ok());
        for entry in entries {
            let entry = match entry {
                Ok(entry) => entry,
                Err(error) => {
                    self.unreadable.push((prefix.to_owned(), error));
                    continue;
                }
            };
            let name = match entry.file_name().into_string() {
                Ok(name) => name,
                Err(name) => {
                    let error = std::io::Error::new(
                        std::io::ErrorKind::InvalidData,
                        "not a UTF-8 file name",
                    );
                    self.unreadable
                        .push((format!("{prefix}{}", name.to_string_lossy()), error));
                    continue;
                }
            };
            let relative = format!("{prefix}{name}");
            let path = dir.join(&name);
            // `metadata` follows symbolic links, so a linked folder is read too.
            match std::fs::metadata(&path) {
                Ok(metadata) if metadata.is_dir() => self.folder(&path, &format!("{relative}/")),
                Ok(_) => match std::fs::read(&path) {
                    Ok(contents) => self.files.insert(relative, contents),
                    Err(error) => self.unreadable.push((relative, error)),
                },
                Err(error) => self.unreadable.push((relative, error)),
            }
        }
    }

    fn folder(&mut self, path: &Path, relative: &str) {
        let refuse = |reason: &str| std::io::Error::new(std::io::ErrorKind::InvalidInput, reason);
        let real = match std::fs::canonicalize(path) {
            Ok(real) => real,
            Err(error) => return self.unreadable.push((relative.to_owned(), error)),
        };
        if self.root.starts_with(&real) {
            return self.unreadable.push((
                relative.to_owned(),
                refuse("links to a folder that holds the package"),
            ));
        }
        if !self.visited.insert(real) {
            return self.unreadable.push((
                relative.to_owned(),
                refuse("links to a folder already read"),
            ));
        }
        match std::fs::read_dir(path) {
            Ok(inner) => self.read(inner, path, relative),
            Err(error) => self.unreadable.push((relative.to_owned(), error)),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn reads_nested_files_with_forward_slashes() {
        let root = std::env::temp_dir().join(format!("esm-package-files-{}", std::process::id()));
        std::fs::create_dir_all(root.join("players/kr")).unwrap();
        std::fs::write(root.join("manifest.json"), "{}").unwrap();
        std::fs::write(root.join("players/kr/kairos.json"), "[]").unwrap();

        let files = PackageFiles::read_dir(&root).unwrap();
        std::fs::remove_dir_all(&root).unwrap();

        let paths: Vec<&str> = files.iter().map(|(path, _)| path).collect();
        assert_eq!(paths, ["manifest.json", "players/kr/kairos.json"]);
    }

    #[test]
    fn a_missing_directory_is_an_error() {
        assert!(PackageFiles::read_dir(Path::new("/definitely/not/here")).is_err());
    }

    #[test]
    fn files_iterate_in_sorted_order() {
        let mut files = PackageFiles::new();
        files.insert("teams/b.json", "1");
        files.insert("teams/a.json", "2");
        files.insert("manifest.json", "3");
        let paths: Vec<&str> = files.iter().map(|(path, _)| path).collect();
        assert_eq!(paths, ["manifest.json", "teams/a.json", "teams/b.json"]);
    }

    #[test]
    fn the_hash_covers_paths_and_contents() {
        let mut one = PackageFiles::new();
        one.insert("a.json", "x");
        let mut renamed = PackageFiles::new();
        renamed.insert("b.json", "x");
        let mut edited = PackageFiles::new();
        edited.insert("a.json", "y");
        let mut split = PackageFiles::new();
        split.insert("a.jso", "nx");

        let hashes = [&one, &renamed, &edited, &split].map(PackageFiles::content_hash);
        for (i, a) in hashes.iter().enumerate() {
            for b in &hashes[i + 1..] {
                assert_ne!(a, b);
            }
        }
        assert_eq!(one.content_hash(), one.clone().content_hash());
    }

    /// Pins the hash so a change to it is deliberate: saves record it.
    #[test]
    fn the_hash_is_pinned() {
        let mut files = PackageFiles::new();
        files.insert("manifest.json", "{}");
        let hex = files
            .content_hash()
            .iter()
            .fold(String::new(), |mut hex, byte| {
                use std::fmt::Write;
                let _ = write!(hex, "{byte:02x}");
                hex
            });
        assert_eq!(
            hex,
            "1403ca0b13a95fe4c2d9fbb85ea908c4c61c18856539735b9673ffeffa47df6d"
        );
    }

    #[cfg(unix)]
    #[test]
    fn links_to_the_package_or_above_it_are_refused() {
        let root = std::env::temp_dir().join(format!("esm-package-links-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&root);
        std::fs::create_dir_all(root.join("teams")).unwrap();
        std::fs::write(root.join("teams/a.json"), "{}").unwrap();
        std::os::unix::fs::symlink("/", root.join("teams/disk")).unwrap();
        std::os::unix::fs::symlink("..", root.join("teams/up")).unwrap();
        let (files, unreadable) = PackageFiles::read_dir_reporting(&root).unwrap();
        std::fs::remove_dir_all(&root).unwrap();
        let paths: Vec<&str> = files.iter().map(|(path, _)| path).collect();
        assert_eq!(paths, ["teams/a.json"]);
        let refused: Vec<&str> = unreadable.iter().map(|(path, _)| path.as_str()).collect();
        assert_eq!(refused, ["teams/disk/", "teams/up/"]);
    }
}
