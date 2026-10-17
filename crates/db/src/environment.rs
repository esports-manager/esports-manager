// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Gathers the real environment for [`app::locations::resolve`], and makes
//! sure the chosen folders can be written (saves spec).

use std::path::{Path, PathBuf};

use app::locations::{
    DataLocations, Environment, LocationError, PORTABLE_MARKER, Platform, resolve,
};

/// The environment of this process, with an optional `--data-dir`.
#[must_use]
pub fn current(data_dir_flag: Option<PathBuf>) -> Environment {
    let executable_dir = std::env::current_exe()
        .ok()
        .and_then(|exe| exe.parent().map(Path::to_path_buf));
    let portable_marker = executable_dir
        .as_ref()
        .is_some_and(|dir| dir.join(PORTABLE_MARKER).is_file());
    Environment {
        data_dir_flag,
        executable_dir,
        portable_marker,
        os_data_dir: dirs::data_dir(),
        platform: platform(),
    }
}

/// The data folders of this process. The CLI and the desktop app both call
/// this, so for the same environment they always agree (SAVE-007).
///
/// # Errors
///
/// When there is no data folder at all.
pub fn locations(data_dir_flag: Option<PathBuf>) -> Result<DataLocations, LocationError> {
    resolve(&current(data_dir_flag))
}

/// Real time, for save timestamps. Adapters are the only place it is read
/// (ADR 0003); both call this.
#[must_use]
pub fn now() -> app::saves::Timestamp {
    #[allow(
        clippy::disallowed_methods,
        reason = "save timestamps are real time, read only by adapters (ADR 0003)"
    )]
    let elapsed = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_or(0, |d| d.as_secs());
    app::saves::Timestamp(i64::try_from(elapsed).unwrap_or(i64::MAX))
}

/// A world seed from OS entropy, for a New Game that doesn't give one.
///
/// # Errors
///
/// When the OS has no entropy to give.
pub fn random_seed() -> Result<u64, getrandom::Error> {
    getrandom::u64()
}

const fn platform() -> Platform {
    if cfg!(target_os = "linux") {
        Platform::Linux
    } else if cfg!(target_os = "windows") {
        Platform::Windows
    } else if cfg!(target_os = "macos") {
        Platform::MacOs
    } else {
        Platform::Other
    }
}

/// Creates the data folders. Portable mode never falls back to the OS
/// folder: if its folder can't be created, this fails, naming it.
///
/// # Errors
///
/// The folder that couldn't be created, and why.
pub fn prepare(locations: &DataLocations) -> Result<(), (PathBuf, std::io::Error)> {
    let saves = locations.saves();
    std::fs::create_dir_all(&saves).map_err(|error| (locations.root().to_path_buf(), error))?;
    // Creating a directory can succeed on a folder we then can't write to.
    // Named per process, so two processes starting at once don't race.
    let probe = saves.join(format!(".write-test-{}", std::process::id()));
    std::fs::write(&probe, b"").map_err(|error| (locations.root().to_path_buf(), error))?;
    std::fs::remove_file(&probe).map_err(|error| (locations.root().to_path_buf(), error))?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn temp(name: &str) -> PathBuf {
        let dir = std::env::temp_dir().join(format!("esm-env-{name}-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&dir);
        dir
    }

    #[test]
    fn the_current_environment_knows_its_platform_and_folders() {
        let environment = current(Some(PathBuf::from("/tmp/x")));
        assert_eq!(environment.data_dir_flag, Some(PathBuf::from("/tmp/x")));
        assert!(environment.executable_dir.is_some());
        assert!(!environment.portable_marker);
        assert_eq!(environment.platform, platform());
        if cfg!(target_os = "linux") {
            assert_eq!(environment.platform, Platform::Linux);
        }
    }

    #[test]
    fn now_is_after_2026_and_seeds_differ() {
        assert!(now().0 > 1_767_225_600);
        assert_ne!(random_seed().unwrap(), random_seed().unwrap());
    }

    #[test]
    fn locations_resolve_the_current_environment() {
        assert_eq!(
            locations(Some(PathBuf::from("/tmp/x"))).unwrap().root(),
            Path::new("/tmp/x")
        );
        assert_eq!(locations(None), resolve(&current(None)));
    }

    #[test]
    fn prepare_creates_the_saves_folder() {
        let root = temp("prepare");
        let locations = resolve(&Environment {
            data_dir_flag: Some(root.clone()),
            executable_dir: None,
            portable_marker: false,
            os_data_dir: None,
            platform: Platform::Linux,
        })
        .unwrap();
        prepare(&locations).unwrap();
        assert!(root.join("saves").is_dir());
        assert_eq!(std::fs::read_dir(root.join("saves")).unwrap().count(), 0);
        std::fs::remove_dir_all(&root).unwrap();
    }

    #[test]
    fn portable_mode_never_falls_back() {
        // spec: SAVE-004
        // Given an executable folder where `data` can't be created, because
        // a file already has that name
        let exe_dir = temp("portable");
        std::fs::create_dir_all(&exe_dir).unwrap();
        std::fs::write(exe_dir.join("data"), b"").unwrap();
        let os_dir = temp("portable-os");
        let locations = resolve(&Environment {
            data_dir_flag: None,
            executable_dir: Some(exe_dir.clone()),
            portable_marker: true,
            os_data_dir: Some(os_dir.clone()),
            platform: Platform::Linux,
        })
        .unwrap();
        // When
        let result = prepare(&locations);
        // Then
        assert_eq!(result.map_err(|(dir, _)| dir), Err(exe_dir.join("data")));
        assert!(!os_dir.exists());
        std::fs::remove_dir_all(&exe_dir).unwrap();
    }
}
