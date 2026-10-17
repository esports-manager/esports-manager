<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# New Game, Load Game and the main menu

- **Prefix:** `NEWG`
- **Status:** Implemented
- **Related:** [packages](packages.md), [world generation](world-generation.md), [saves](saves.md), [roster](roster.md), [ADR 0006](../adr/0006-bindings-and-pure-view.md)

## Summary

The front door of the game. The main menu leads to New Game or Load Game. New Game asks for a manager name, a team and a save name, then builds a world from the core package and a seed. Load Game lists the saves. Both end on the roster of the user's team. The CLI offers the same use cases, and is the backbone of the backend's end-to-end tests.


## Rules

### Use cases (`app`)

- **`new_game_options()`** returns the regions, each with its name message id, its league (competition id and name message id) for the tab label, and its teams as `TeamOption`s. Each team has:
  - id, name message id, tag and colours
  - **strength**: 1–5 stars, the ceiling of reputation / 20
- **`new_game(request)`** takes the manager name, team id, save name and seed. In order, it:
  1. loads and validates the core package; any error ends here with the report
  2. generates the world
  3. creates the save
  4. returns the save's id and the user's team
- **`list_saves()`** and **`open_save(id)`**: see [saves](saves.md).

### Validation (`app`; errors are codes with typed arguments)

- **Manager name:** trimmed, 1 to 32 characters, with no control characters.
- **Save name:** trimmed, 1 to 48 characters, with no control characters, unique among saves ignoring case. It defaults to the team's name in the UI.
- "Control characters" includes invisible ones that hide or reorder text: zero-width spaces, bidirectional controls and the byte-order mark. The zero-width joiner and non-joiner are allowed, since names in some scripts and emoji need them. A name with no visible character is empty.
- **Team:** must exist in the loaded content.
- **Characters** are Unicode scalar values (Rust's `chars()`), never bytes, so "Ana Júlia" is 9 characters. The UI doesn't count them itself, and sets no `maxlength`; it shows the backend's errors.
- Every error is reported, not just the first, and nothing is written.

### Seed

- **By default, the adapter draws the seed from OS entropy** (`getrandom`) and passes it in as a `WorldSeed`. The domain never draws it.
- The CLI takes `--seed <u64>`. The UI's New Game has a collapsed **Advanced** section with an optional seed field.
- The seed is stored in `save_meta` with the packages' ids, versions and content hashes, so the same world can be generated again with the same packages and game version.

### Flow (UI)

- **Main menu:** New Game, Load Game, Quit. Quit is desktop only.
- **New Game** is a three-step wizard, and each step can go back without losing input:
  1. **Manager**
  2. **Team:** one tab per region, with team cards inside
  3. **Confirm:** save name, Advanced, and Start
- Start shows a progress state until the use case returns, then opens the user's team's [roster](roster.md). If package validation fails, the report is shown instead, with each error's file and path.
- **Load Game** lists saves with name, manager, team, game date and last played. Damaged saves are shown but can't be opened. Choosing a save opens the roster.

## UI

### Main menu

```
Wide (≥ 1024 px)                          Compact (< 640 px)
┌──────────────────────────────────────┐  ┌──────────────────┐
│                                      │  │  eSports Manager │
│           eSports Manager            │  │  v0.0.0          │
│               v0.0.0                 │  │                  │
│                                      │  │ [   New Game   ] │
│         [   New Game    ]            │  │ [   Load Game  ] │
│         [   Load Game   ]            │  │                  │
│         [     Quit      ]            │  │                  │
└──────────────────────────────────────┘  └──────────────────┘
```

### New Game, step 2: Team

```
Wide
┌──────────────────────────────────────────────────────────────┐
│ ← Back      New Game · 2 of 3 · Choose your team             │
│ [ Seorabeol Pro League ] [ Liga Pindorama ]   ← region tabs  │
│ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐  │
│ │ (AZT)      │ │ (CDY)      │ │ (MRG)      │ │ (ICR)      │  │
│ │ Azure      │ │ Crimson    │ │ Moonrise   │ │ Iron       │  │
│ │ Tigers     │ │ Dynasty    │ │ Gaming     │ │ Cranes     │  │
│ │ ★★★★★      │ │ ★★★★★      │ │ ★★★★★      │ │ ★★★★☆      │  │
│ └────────────┘ └────────────┘ └────────────┘ └────────────┘  │
│  … one card per team, a grid of 4 to 5 columns               │
│                                                  [ Next → ]  │
└──────────────────────────────────────────────────────────────┘

Compact
┌──────────────────────┐
│ ← 2 of 3 · Team      │
│ [Seorabeol][Pindor…] │
│ ┌──────────────────┐ │
│ │(AZT) Azure Tigers│ │
│ │      ★★★★★       │ │
│ └──────────────────┘ │
│ ┌──────────────────┐ │
│ │(CDY) Crimson Dyn.│ │
│ └──────────────────┘ │
│  … one card per row  │
│ [      Next →      ] │
└──────────────────────┘
```

- `(AZT)` is the team's crest: a monogram of its tag in its colours ([roster](roster.md)).
- The cards are a radio group. Arrow keys move between them, and Space or Enter selects one. Every card is at least 44 px tall.
- Steps 1 and 3 are single-column forms in both layouts.

### Load Game

```
Wide                                                    Compact
┌───────────────────────────────────────────────────┐   ┌───────────────────┐
│ ← Back                 Load Game                  │   │ ← Load Game       │
│ Name          Manager  Team          Date  Played │   │ Ana's Tigers      │
│ Ana's Tigers  Ana      Azure Tigers  1 Jan  today │   │ Ana · AZT · today │
│ Test world    Bo       Onça Gaming   1 Jan  2 d   │   │───────────────────│
│ broken        ⚠ damaged: not a save file          │   │ ⚠ broken: damaged │
└───────────────────────────────────────────────────┘   └───────────────────┘
```

## CLI

Global options: `--data-dir <path>`; `--content <dir>`, the package New Game builds from (default `content/core`, relative to the working directory; the desktop app bundles it); `--locale <en|pt-BR>`, default `en`; and `--json`, which prints the use case's view DTO as JSON. Text output goes through Fluent, with the game's catalogs from `src/locales` built into the binary (ADR 0007). Tests use `--json`. Help text (`--help`) is clap's and stays in English.

```
esm teams                                        list team ids by region, for --team
esm new-game --manager <name> --team <team-id> --save <name> [--seed <u64>]
esm saves                                        list saves (see the saves spec)
```

Exit code 0 on success, 1 on a validation or use-case error, 2 on bad arguments.

## Scenarios

### NEWG-001 — New Game offers both regions and their teams

- **Given** the core package
- **When** the New Game options are requested
- **Then** they list the Seorabeol region with 10 teams and the Pindorama region with 8, each with its league's name. Each team has a name, a tag, two colours and a strength of 1 to 5 stars

### NEWG-002 — Strength stars come from reputation

- **Given** teams with reputations 95, 41 and 1
- **When** their New Game options are built
- **Then** their strengths are 5, 3 and 1 stars

### NEWG-003 — A new game creates a save for the chosen team

- **Given** an empty data folder
- **When** a new game is started with manager "Ana", team `team:azure_tigers` and save name "Ana's Tigers"
- **Then** the save exists, and its user team is `team:azure_tigers` with a seven-player roster

### NEWG-004 — A given seed reproduces the world

- **Given** a game created by `esm new-game --seed 42`
- **When** a second game is created with `--seed 42` under another save name
- **Then** `esm roster --json` prints identical rosters for the two saves

### NEWG-005 — Without a seed, each game gets its own world

- **Given** an empty data folder
- **When** two games are created without `--seed`
- **Then** their recorded seeds differ, and each save's `save_meta` holds its seed

### NEWG-006 — Invalid requests write nothing, and report every error

- **Given** an empty data folder
- **When** a new game is started with a blank manager name and team `team:nowhere`
- **Then** the result has an empty-manager-name error and an unknown-team error, and `saves/` is empty

### NEWG-007 — A broken package shows its report

- **Given** a core package with a validation error
- **When** a new game is started in the UI
- **Then** the validation report is shown with the error's file and path, and no save is created

### NEWG-008 — The wizard ends on the roster

- **Given** the main menu
- **When** the user enters a manager name, picks a team and starts
- **Then** the roster of that team is shown

### NEWG-009 — The wizard works with the keyboard alone

- **Given** the main menu
- **When** the user completes New Game using only Tab, the arrow keys, Space and Enter
- **Then** the roster is shown

### NEWG-010 — Going back keeps what was typed

- **Given** the New Game wizard on step 2, with manager name "Ana"
- **When** the user goes back to step 1
- **Then** the manager name field still holds "Ana"

### NEWG-011 — Load Game opens a save on its roster

- **Given** two saves in the data folder
- **When** the user opens Load Game and picks one
- **Then** the roster of that save's user team is shown

### NEWG-012 — `esm teams` lists the ids `new-game` accepts

- **Given** the core package
- **When** `esm teams --json` runs
- **Then** it lists 18 team ids grouped by region, and `esm new-game --team` accepts each of them

### NEWG-013 — Both layouts pass the accessibility audit

- **Given** the main menu, each New Game step and Load Game
- **When** each is shown in the wide and the compact layout
- **Then** axe reports no violations, and the page doesn't scroll horizontally
