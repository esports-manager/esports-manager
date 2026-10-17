// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! One process at a time per save (saves spec), through an OS lock on a file
//! next to it: `tigers.esmsave.lock`.
//!
//! The lock lives in its own file, never on the database: on Windows a lock
//! on the `.esmsave` would collide with SQLite's own byte-range locks. The OS
//! releases it when the process ends, so a crash never leaves a save locked.
//! A lock file is never deleted while its save exists: another process may
//! have it open, and deleting it would let a third lock a fresh one.

use std::fs::{File, TryLockError};
use std::path::{Path, PathBuf};

use app::saves::SaveError;

/// The lock file of `path`.
pub(super) fn lock_path(path: &Path) -> PathBuf {
    let mut name = path.as_os_str().to_owned();
    name.push(".lock");
    PathBuf::from(name)
}

/// How often, and how far apart, `acquire` tries before calling a save in
/// use: another process may be checking the lock (`is_held`) for a moment.
const TRIES: u32 = 10;
const PAUSE: std::time::Duration = std::time::Duration::from_millis(20);

fn open(path: &Path) -> Result<File, SaveError> {
    File::options()
        .read(true)
        .write(true)
        .create(true)
        .truncate(false)
        .open(lock_path(path))
        .map_err(|e| SaveError::Storage(e.to_string()))
}

/// Takes the lock of `path`, or fails with `InUse` if another holder keeps
/// it. The lock lasts as long as the returned file.
pub(super) fn acquire(path: &Path) -> Result<File, SaveError> {
    let file = open(path)?;
    for _ in 1..TRIES {
        match file.try_lock() {
            Ok(()) => return Ok(file),
            Err(TryLockError::WouldBlock) => std::thread::sleep(PAUSE),
            Err(TryLockError::Error(error)) => return Err(SaveError::Storage(error.to_string())),
        }
    }
    match file.try_lock() {
        Ok(()) => Ok(file),
        Err(TryLockError::WouldBlock) => Err(SaveError::InUse),
        Err(TryLockError::Error(error)) => Err(SaveError::Storage(error.to_string())),
    }
}

/// Takes the lock of `path`, waiting for any other holder to let go.
pub(super) fn wait(path: &Path) -> Result<File, SaveError> {
    let file = open(path)?;
    file.lock().map_err(|e| SaveError::Storage(e.to_string()))?;
    Ok(file)
}

/// Whether someone holds the lock of `path`, this process included. A save
/// without a lock file was never opened, so it isn't in use. The check takes
/// a shared lock, so two processes checking never block each other.
pub(super) fn is_held(path: &Path) -> bool {
    let Ok(file) = File::options().read(true).write(true).open(lock_path(path)) else {
        return false;
    };
    matches!(file.try_lock_shared(), Err(TryLockError::WouldBlock))
}
