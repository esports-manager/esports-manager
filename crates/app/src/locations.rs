// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Where the game keeps its files (saves spec).
//!
//! The choice is one pure function of the environment, so the CLI and the
//! desktop app always agree on the folder. The adapters only gather the
//! environment.

use std::path::{Path, PathBuf};

/// The folder name under the OS data folder.
pub const DATA_FOLDER: &str = "esports-manager";
/// A file next to the executable that turns on portable mode.
pub const PORTABLE_MARKER: &str = "portable";
/// The data folder's name next to the executable in portable mode.
pub const PORTABLE_FOLDER: &str = "data";

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Platform {
    Linux,
    Windows,
    MacOs,
    Other,
}

impl Platform {
    /// Whether portable mode exists here. On macOS the webview's data can't
    /// leave `~/Library`, and app translocation runs apps from a random
    /// read-only path, so the marker is ignored.
    #[must_use]
    pub const fn supports_portable(self) -> bool {
        match self {
            Self::Linux | Self::Windows | Self::Other => true,
            Self::MacOs => false,
        }
    }
}

/// What the adapters gather from the real environment.
#[derive(Debug, PartialEq, Eq)]
pub struct Environment {
    /// `--data-dir`, from the CLI.
    pub data_dir_flag: Option<PathBuf>,
    pub executable_dir: Option<PathBuf>,
    /// Whether `portable` exists next to the executable.
    pub portable_marker: bool,
    /// The OS data folder, such as `~/.local/share`.
    pub os_data_dir: Option<PathBuf>,
    pub platform: Platform,
}

/// The folders the game uses.
#[derive(Debug, PartialEq, Eq)]
pub struct DataLocations {
    root: PathBuf,
    portable: bool,
}

#[derive(Debug, PartialEq, Eq, thiserror::Error)]
pub enum LocationError {
    #[error("there is no data folder: the OS reports none and no --data-dir was given")]
    NoDataFolder,
}

impl DataLocations {
    #[must_use]
    pub fn root(&self) -> &Path {
        &self.root
    }

    #[must_use]
    pub const fn is_portable(&self) -> bool {
        self.portable
    }

    #[must_use]
    pub fn saves(&self) -> PathBuf {
        self.root.join("saves")
    }

    /// The webview's own data folder, in portable mode only. Otherwise the
    /// webview keeps its default.
    #[must_use]
    pub fn webview(&self) -> Option<PathBuf> {
        self.portable.then(|| self.root.join("webview"))
    }
}

/// Picks the data folder: `--data-dir`, else the portable folder when the
/// marker is present and the platform supports it, else the OS data folder.
///
/// # Errors
///
/// When none of those exists.
pub fn resolve(environment: &Environment) -> Result<DataLocations, LocationError> {
    if let Some(dir) = &environment.data_dir_flag {
        return Ok(DataLocations {
            root: dir.clone(),
            portable: false,
        });
    }
    if environment.portable_marker
        && environment.platform.supports_portable()
        && let Some(dir) = &environment.executable_dir
    {
        return Ok(DataLocations {
            root: dir.join(PORTABLE_FOLDER),
            portable: true,
        });
    }
    environment
        .os_data_dir
        .as_ref()
        .map(|dir| DataLocations {
            root: dir.join(DATA_FOLDER),
            portable: false,
        })
        .ok_or(LocationError::NoDataFolder)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn linux() -> Environment {
        Environment {
            data_dir_flag: None,
            executable_dir: Some(PathBuf::from("/games/esm")),
            portable_marker: false,
            os_data_dir: Some(PathBuf::from("/home/ana/.local/share")),
            platform: Platform::Linux,
        }
    }

    #[test]
    fn the_os_data_folder_is_the_default() {
        // spec: SAVE-001
        // Given
        let environment = linux();
        // When
        let locations = resolve(&environment).unwrap();
        // Then
        assert_eq!(
            locations.root(),
            Path::new("/home/ana/.local/share/esports-manager")
        );
        assert!(!locations.is_portable());
        assert_eq!(
            locations.saves(),
            PathBuf::from("/home/ana/.local/share/esports-manager/saves")
        );
        assert_eq!(locations.webview(), None);
    }

    #[test]
    fn the_portable_marker_keeps_everything_next_to_the_executable() {
        // spec: SAVE-002
        for platform in [Platform::Linux, Platform::Windows] {
            // Given
            let environment = Environment {
                portable_marker: true,
                platform,
                ..linux()
            };
            // When
            let locations = resolve(&environment).unwrap();
            // Then
            assert_eq!(locations.root(), Path::new("/games/esm/data"));
            assert!(locations.is_portable());
            assert_eq!(
                locations.webview(),
                Some(PathBuf::from("/games/esm/data/webview"))
            );
        }
    }

    #[test]
    fn the_data_dir_flag_wins() {
        // spec: SAVE-003
        // Given
        let environment = Environment {
            data_dir_flag: Some(PathBuf::from("/tmp/world")),
            portable_marker: true,
            ..linux()
        };
        // When
        let locations = resolve(&environment).unwrap();
        // Then
        assert_eq!(locations.root(), Path::new("/tmp/world"));
        assert!(!locations.is_portable());
    }

    #[test]
    fn the_marker_is_ignored_on_macos() {
        // spec: SAVE-005
        // Given
        let environment = Environment {
            portable_marker: true,
            os_data_dir: Some(PathBuf::from("/Users/ana/Library/Application Support")),
            platform: Platform::MacOs,
            ..linux()
        };
        // When
        let locations = resolve(&environment).unwrap();
        // Then
        assert_eq!(
            locations.root(),
            Path::new("/Users/ana/Library/Application Support/esports-manager")
        );
    }

    #[test]
    fn portable_mode_needs_the_executables_folder() {
        let environment = Environment {
            portable_marker: true,
            executable_dir: None,
            ..linux()
        };
        assert!(!resolve(&environment).unwrap().is_portable());
    }

    #[test]
    fn without_any_folder_there_is_an_error() {
        let environment = Environment {
            os_data_dir: None,
            ..linux()
        };
        assert_eq!(resolve(&environment), Err(LocationError::NoDataFolder));
    }

    #[test]
    fn other_platforms_support_portable_mode() {
        assert!(Platform::Other.supports_portable());
    }
}
