<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Saves and data locations

- **Prefix:** `SAVE`
- **Status:** Implemented
- **Related:** [ADR 0001](../adr/0001-clean-architecture-and-workspace-layout.md), [ADR 0004](../adr/0004-sqlite-and-diesel.md), [new game](new-game.md)

## Summary

A save is one SQLite file, and it is the world (ADR 0004). This spec fixes where the game keeps its files, including a **portable mode** where everything lives in one folder next to the executable, and how saves are created, listed and opened. The CLI and the desktop app find the same folder, so a save made in one can be played in the other.

## Rules

### Data folder (`app` resolves it, `db` gathers the environment)

The data folder is chosen in this order:

1. **`--data-dir <path>`** (CLI only): that folder.
2. **Portable mode:** a file named `portable` next to the executable, with any content, makes the data folder `<executable folder>/data/`.
3. **Otherwise, the OS data folder:** `dirs::data_dir()` joined with `esports-manager`:
   - Linux: `$XDG_DATA_HOME/esports-manager`, by default `~/.local/share/esports-manager`
   - Windows: `%APPDATA%\esports-manager`
   - macOS: `~/Library/Application Support/esports-manager`

How the folder is picked is decided in one pure function in `app`. Its inputs are the flag, whether the marker exists, the executable's folder and the OS data folder. `db` gathers those inputs from the real environment, and both adapters call the same code. Tauri's own path API is not used for this, because its folder is named after the bundle identifier and would differ from the CLI's.

**Portable mode never falls back.** If the portable folder can't be created or written, starting fails with an error naming the folder. Saves never end up scattered between two places.

**Platforms:**

- **Windows and Linux:** portable builds ship as a zip and a tarball. The desktop app also points the webview's own data (cache, storage) at `<data>/webview/`, so nothing is written outside the folder.
- **macOS:** no portable build. WKWebView can't move its data out of `~/Library`, and macOS app translocation runs downloaded apps from a random read-only path, which breaks "next to the executable". The marker is ignored on macOS.

### Folder layout

```
<data>/
  saves/      one .esmsave file per save
  webview/    portable mode only (Windows, Linux)
  packages/   user packages, later
```

### Save files (`db`)

- **One SQLite file per save:** `<data>/saves/<file name>.esmsave`.
- **The display name** is what the user typed. It must be unique among saves, ignoring case, and it is stored in the save. The file name is the name's slug (lowercase ASCII letters, digits and `-`), with `-2`, `-3`, … added if a different save already uses that slug. A name with no ASCII letters or digits, such as "호랑이", gets the slug `save`.
- **Length limits** count Unicode scalar values, not bytes. The UI doesn't enforce them itself; it shows the backend's errors.
- **`save_meta`** is a one-row table in every save:
  - display name, manager name, team id, genre
  - world seed, and each package's id, version and content hash
  - the game version that created the save
  - current game date
  - `created_at` and `last_played_at`, which are real time supplied by the adapter, never read by the domain
- The package text needed to show the world is copied into the save at New Game ([packages](packages.md)).
- **The schema version** is the save's latest applied migration, which Diesel records in `__diesel_schema_migrations` in the same file (ADR 0004). `save_meta` doesn't repeat it: one copy can't disagree with another, and the version check reads it before anything else in the file.

### Creating

- A new save is written to a temporary file whose name is unique to that attempt (`<file name>.<attempt>.tmp`), in one transaction, then moved into place.
- **Moving never replaces an existing file.** If the final name appeared in the meantime, creation fails with a name-taken error, and the other save is untouched.
- If anything fails, the temporary file is removed and no save appears in the list. A `.tmp` file left by a crash is removed the next time the game starts, unless another process holds it open.

### Listing (`db`, through the `app` port)

- **The list is built by scanning `saves/*.esmsave`** and reading each file's `save_meta`. There is no separate index to drift, and a save copied into the folder by hand shows up.
- It is sorted by `last_played_at`, newest first, then by display name, then by file name, so the order is the same on every run.
- A file that can't be read is listed as damaged, with a reason (not a database, missing `save_meta`, newer schema). The other saves are still listed, and the list never fails because of one file.
- `.tmp` files are ignored.

### Opening

- **One process at a time.** An open save is held exclusively by the process that opened it, through an OS lock on a file beside it (`tigers.esmsave.lock`). The OS releases the lock when the process ends, so a crash never leaves a save locked. Opening a save that the CLI or another window already has open is refused with a save-in-use error. Its metadata can still be read, so Load Game lists it in its place, marked as open elsewhere. This also means two processes never interleave writes to one world. Creating a save takes a lock on the folder (`saves/.create.lock`) from checking the name to moving the file into place, so two processes creating at once can't both take the same name.
- Opening a save sets `last_played_at`.
- A save whose schema version is newer than the game's is refused with an error saying it was made by a newer version. Older saves are migrated (ADR 0004); there are none yet.
- Deleting and renaming saves come later.

## Data

`save_meta` is game-owned, not moddable. The `.esmsave` format is SQLite with Diesel migrations (ADR 0004).

## Scenarios

### SAVE-001 — The OS data folder is the default

- **Given** no `--data-dir` and no `portable` file next to the executable, on Linux with `XDG_DATA_HOME` unset and home `/home/ana`
- **When** the data folder is resolved
- **Then** it is `/home/ana/.local/share/esports-manager`

### SAVE-002 — The portable marker keeps everything next to the executable

- **Given** an executable in `/games/esm/` with a file `/games/esm/portable`, on Windows or Linux
- **When** the data folder is resolved
- **Then** it is `/games/esm/data`

### SAVE-003 — `--data-dir` wins

- **Given** a `portable` file next to the CLI executable
- **When** the CLI runs with `--data-dir /tmp/world`
- **Then** the data folder is `/tmp/world`

### SAVE-004 — Portable mode never falls back

- **Given** portable mode, and an executable folder that can't be written
- **When** the game starts
- **Then** it fails with an error naming `<executable folder>/data`, and nothing is written to the OS data folder

### SAVE-005 — The marker is ignored on macOS

- **Given** a `portable` file next to the executable, on macOS
- **When** the data folder is resolved
- **Then** it is the OS data folder

### SAVE-006 — Portable desktop keeps webview data inside the folder

- **Given** the desktop app in portable mode on Windows or Linux
- **When** its main window is built
- **Then** the webview's data folder is `<data>/webview`

### SAVE-007 — The CLI and the desktop app agree

- **Given** the same environment (executable folder, marker, OS data folder)
- **When** the CLI and the desktop app each resolve the data folder
- **Then** both get the same folder

### SAVE-008 — A new save is one file with its metadata

- **Given** an empty data folder
- **When** a new game named "Ana's Tigers" is created
- **Then** `saves/ana-s-tigers.esmsave` exists, and its `save_meta` has that display name, the manager, the team, the genre, the seed, the game version and the start date, and the file records every migration as applied

### SAVE-009 — A failed creation leaves nothing behind

- **Given** an empty data folder
- **When** creating a new save fails after its file was started
- **Then** `saves/` contains no `.esmsave` and no `.tmp` file

### SAVE-010 — Save names are unique, ignoring case

- **Given** a save named "Tigers"
- **When** a new game named "tigers" is created
- **Then** it is refused with a name-taken error, and the existing save is unchanged

### SAVE-011 — Different names with the same slug get distinct files

- **Given** a save named "Tigers!" in `saves/tigers.esmsave`
- **When** a new game named "Tigers?" is created
- **Then** it is written to `saves/tigers-2.esmsave`

### SAVE-012 — The list comes from the folder, newest first

- **Given** two saves last played on different days, and a third save file copied into `saves/` by hand
- **When** the saves are listed
- **Then** all three are listed, sorted by last played, newest first

### SAVE-013 — A damaged file doesn't break the list

- **Given** a valid save and a file `saves/broken.esmsave` that isn't a database
- **When** the saves are listed
- **Then** the valid save is listed normally, and `broken.esmsave` is listed as damaged with reason "not a save file"

### SAVE-014 — Newer saves are refused

- **Given** a save whose schema version is higher than the game's
- **When** it is opened
- **Then** it is refused with a made-by-a-newer-version error, and the file is unchanged

### SAVE-015 — A save round-trips

- **Given** a new game whose roster view has been read
- **When** the game is closed, and the save is opened again in a new process
- **Then** the roster view is identical

### SAVE-016 — Opening updates last played

- **Given** a save last played at 10:00
- **When** it is opened at 12:00
- **Then** its `last_played_at` is 12:00

### SAVE-017 — A name with no ASCII letters still gets a file

- **Given** an empty data folder
- **When** a new game named "호랑이" is created
- **Then** it is written to `saves/save.esmsave`, and listed as "호랑이"

### SAVE-018 — Creation never replaces an existing save

- **Given** a creation whose final file `saves/tigers.esmsave` appears before it moves its temporary file into place
- **When** it finishes
- **Then** it fails with a name-taken error, and the existing `tigers.esmsave` is unchanged

### SAVE-019 — A crash's leftovers are cleaned up

- **Given** a `.tmp` file in `saves/` left by a crashed creation
- **When** the game starts
- **Then** the file is removed, and a new game with the same name succeeds

### SAVE-020 — An open save can't be opened twice

- **Given** a save that the CLI has open
- **When** the desktop app tries to open it
- **Then** it is refused with a save-in-use error

### SAVE-021 — Saves played at the same moment have a stable order

- **Given** two saves named "Beta" and "Alpha" with the same `last_played_at`
- **When** the saves are listed twice
- **Then** both lists show "Alpha" before "Beta"

## Enforcement

These land with the code in the implementing PR:

- **Migration fixtures (ADR 0004):** the first migration gets its fixture save, and every later migration is tested by opening the previous fixture.
- **Ordered-query helper (ADR 0003):** listing and every repository query that returns a collection goes through the helper. Review checks it.
- **Desktop coverage:** `src-tauri` is exactly at its 60% minimum, so the new commands come with tests, or the gate fails.

## Open questions

- Portable builds don't move existing OS-folder saves into their folder; users copy the files.
- Settings (language, delegation defaults) and logs: where they live comes with the settings screen.
