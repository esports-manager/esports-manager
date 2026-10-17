// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

use super::write::{commit, commit_with};
use super::*;

fn folder(name: &str) -> PathBuf {
    let dir = std::env::temp_dir().join(format!("esm-db-unit-{name}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&dir);
    std::fs::create_dir_all(&dir).unwrap();
    dir
}

#[test]
fn creation_never_replaces_an_existing_save() {
    // spec: SAVE-018
    // Given a finished temporary save, and a save that appeared under
    // its final name in the meantime
    let dir = folder("commit");
    let (temporary, target) = (dir.join("tigers.1-0.tmp"), dir.join("tigers.esmsave"));
    std::fs::write(&temporary, b"new").unwrap();
    std::fs::write(&target, b"existing").unwrap();
    // When
    let result = commit(&temporary, &target, "Tigers");
    // Then
    assert_eq!(result, Err(SaveError::NameTaken("Tigers".to_owned())));
    assert_eq!(std::fs::read(&target).unwrap(), b"existing");
}

#[test]
fn without_hard_links_commit_copies_but_never_replaces() {
    let dir = folder("commit-fat");
    let no_links = |_: &Path, _: &Path| Err(std::io::Error::other("no hard links here"));
    let (temporary, target) = (dir.join("a.1-0.tmp"), dir.join("a.esmsave"));
    std::fs::write(&temporary, b"new").unwrap();
    assert_eq!(commit_with(no_links, &temporary, &target, "A"), Ok(()));
    assert_eq!(std::fs::read(&target).unwrap(), b"new");
    assert!(!temporary.exists());
    // A save that appears under the name first wins; nothing replaces it.
    std::fs::write(&temporary, b"newer").unwrap();
    assert_eq!(
        commit_with(no_links, &temporary, &target, "A"),
        Err(SaveError::NameTaken("A".to_owned()))
    );
    assert_eq!(std::fs::read(&target).unwrap(), b"new");
    // A failed copy leaves no half-written save behind.
    let missing = dir.join("missing.tmp");
    let target = dir.join("b.esmsave");
    assert!(matches!(
        commit_with(no_links, &missing, &target, "B"),
        Err(SaveError::Storage(_))
    ));
    assert!(!target.exists());
}

#[test]
fn a_link_that_finds_the_target_taken_is_name_taken() {
    let dir = folder("commit-taken");
    let exists = |_: &Path, _: &Path| Err(std::io::Error::from(std::io::ErrorKind::AlreadyExists));
    let (temporary, target) = (dir.join("a.1-0.tmp"), dir.join("a.esmsave"));
    std::fs::write(&temporary, b"new").unwrap();
    assert_eq!(
        commit_with(exists, &temporary, &target, "A"),
        Err(SaveError::NameTaken("A".to_owned()))
    );
    assert!(!target.exists());
}

#[test]
fn commit_moves_the_temporary_file_into_place() {
    let dir = folder("commit-ok");
    let (temporary, target) = (dir.join("a.1-0.tmp"), dir.join("a.esmsave"));
    std::fs::write(&temporary, b"new").unwrap();
    assert_eq!(commit(&temporary, &target, "A"), Ok(()));
    assert_eq!(std::fs::read(&target).unwrap(), b"new");
    assert!(!temporary.exists());
}

#[test]
fn a_temporary_file_still_being_written_is_kept() {
    let dir = folder("in-use-tmp");
    let path = dir.join("busy.1-0.tmp");
    std::fs::write(&path, b"half a save").unwrap();
    let held = lock::acquire(&path).unwrap();
    drop(SqliteSaveStore::new(dir.clone()));
    assert!(path.exists());
    drop(held);
    std::fs::write(journal(&path), b"").unwrap();
    drop(SqliteSaveStore::new(dir));
    assert!(!path.exists());
    assert!(!journal(&path).exists());
    assert!(!lock::lock_path(&path).exists());
}

#[test]
fn a_lock_is_exclusive_and_ends_with_its_holder() {
    let dir = folder("lock");
    let path = dir.join("a.esmsave");
    assert!(!lock::is_held(&path), "no lock file means not in use");
    let held = lock::acquire(&path).unwrap();
    assert!(lock::is_held(&path));
    assert_eq!(lock::acquire(&path).map(|_| ()), Err(SaveError::InUse));
    drop(held);
    assert!(!lock::is_held(&path));
    assert!(lock::acquire(&path).is_ok());
}

#[test]
fn only_plain_save_names_are_accepted() {
    assert!(is_save_name("tigers.esmsave"));
    for name in [
        "../tigers.esmsave",
        "a/tigers.esmsave",
        "tigers.txt",
        "tigers",
        "",
        ".",
    ] {
        assert!(!is_save_name(name), "{name}");
    }
    if cfg!(windows) {
        assert!(!is_save_name("C:tigers.esmsave"));
        assert!(!is_save_name("a\\tigers.esmsave"));
    }
}

#[test]
fn non_utf8_paths_are_refused() {
    #[cfg(unix)]
    {
        use std::os::unix::ffi::OsStrExt;
        let path = Path::new(std::ffi::OsStr::from_bytes(b"/tmp/\xff.esmsave"));
        assert!(matches!(meta::connect(path), Err(SaveError::Storage(_))));
    }
}
