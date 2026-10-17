<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Content packages

- **Prefix:** `PKG`
- **Status:** Implemented
- **Related:** [ADR 0005](../adr/0005-esm-packages.md), [ADR 0007](../adr/0007-i18n-fluent.md), [ADR 0010](../adr/0010-fictional-world-and-licensing.md), [world generation](world-generation.md)

## Summary

A content package is how a world gets into the game. The base game is the package at `content/core`, and it goes through the same loader as any user package. This spec fixes the package's layout, how files map to content types, how ids work, and what the loader reports when something is wrong. The walking skeleton loads `content/core` only. Choosing user packages at New Game, `.zip` packages and override-by-id across packages come later, in their own spec.

## Rules

### Layout (`packages`)

A package is a directory. Its root holds `manifest.json`, and each **top-level folder names one content type**:

```
content/core/
  manifest.json
  world.json                      start date
  regions/          *.json        regions and their nationality mix
  nationalities/    *.json        countries, codes, name order
  name-pools/       *.json        given and family names per nationality
  nicknames/        *.json        nickname pools, merged into one
  competitions/     *.json        leagues (stages come with the competitions spec)
  teams/            **/*.json     teams
  players/          **/*.json     pinned players (any subset of fields)
  roles/            *.json        the role set with its overall weights, and the roster's subs
  generation/       *.json        the generator's constants
  locales/en/       *.ftl         the package's own text
  locales/pt-BR/    *.ftl
```

- **Any number of files, in any subfolders.** `players/kr/kairos.json` and `players/all.json` are both fine. File and folder names carry no meaning below the type folder.
- **A file holds one entity or a list of entities** of its folder's type.
- **Files are read in sorted path order** (byte order of the path relative to the package root), so the loaded order and the order of reported errors are the same on every OS.
- **An unknown top-level folder is an error**, so a typo like `team/` is reported instead of silently ignored. `locales/` is the only folder that doesn't hold JSON.
- **Nothing else sits at the root**, licence files included: a package's licence is its manifest's `license` field (ADR 0011).
- Genre-specific types (`roles/`, `generation/` and `players/` today, `champions/` later) are defined by the genre module named in the manifest (`esports::moba`). Generic types (`regions/`, `teams/`, …) are defined in `packages` and converted into `domain` types.

### Ids (`packages`)

- **Every entity has an `id` field** of the form `<kind>:<slug>`, for example `team:azure_tigers`. The slug uses `a-z`, `0-9` and `_`.
- **The id comes from the field, never from the file name.** Renaming or moving a file never changes identity.
- The kind must match the folder: a `team:` id in `players/` is an error.
- **Two entities with the same id in one package are an error** that names both files.
- References between entities use ids (`"region": "region:seorabeol"`). A reference to an id that doesn't exist is an error.
- At load time, string ids resolve to compact typed ids. String ids are what the save stores as the stable identity of package content.
- Generated players get ids containing `.`, which package slugs can't contain ([world generation](world-generation.md)).

### Validation (`packages`, messages in the UI catalog)

- **Unknown fields are errors** (`deny_unknown_fields`), so a misspelt field never silently falls back to a default.
- **The loader collects every error** in the package, not just the first.
- Each error has a code, the file, the JSON path within the file, and typed arguments. The UI and the CLI render it through Fluent (ADR 0007); the loader never produces prose.
- If a package has any error, nothing is generated and no save is written.
- Besides the format rules here, the loader checks that the content can be generated from: nationality mixes, name pools, the role set, nicknames and pinned rosters ([world generation](world-generation.md)). New Game never fails part-way because of package content.

### Text (`packages`, rendered by the UI)

- **Names that can be translated are Fluent messages** in the package's `locales/<locale>/*.ftl`: regions, competitions, teams, nationalities and roles. Each one's message id is derived from its entity id by one rule: replace `:` with `-` (`team:azure_tigers` → `team-azure_tigers`).
- **People's names are data**, written in the JSON or drawn from name pools. They are proper nouns and are never translated.
- A package declares the locales it supports in its manifest. Every derived message must exist in the package's first declared locale; a missing one is an error. A message missing in another locale falls back to that first locale when shown.
- At New Game, the package's `.ftl` text is copied into the save, so a save keeps working if the package is later removed. The UI loads it from the save with its own catalogs.

### Manifest (`packages`)

`manifest.json` declares `id`, `version` (`major.minor.patch`), `title`, `license` (SPDX expression), `authors`, `genre` (`moba`) and `locales`. ADR 0005 also lists dependencies and load order. Those fields are added with user packages, when something reads them: while only core loads they would be validated and then ignored, which ADR 0005 exists to prevent.

A package defines exactly one world, one role set and one set of generator constants.

### Schemas (`packages`)

JSON Schemas are generated from the Rust package types with `schemars` and committed under `content/schemas/`. Each content type's schema accepts one entity or a list.

- **A file that holds one object** may carry a top-level `$schema` field pointing at its schema. The loader accepts and skips it: it is editor metadata, not content. It is the only field allowed besides the type's own.
- **A file that holds a list** can't carry `$schema`, because its top level is an array. An editor can still associate the schema by path (for example VS Code's `json.schemas` setting mapping `teams/**/*.json` to `team.schema.json`). Every file in `content/core` holds one object and carries `$schema`.

## Data

| Type | Folder | Key fields (all moddable) |
|---|---|---|
| World | `world.json` | `start_date` |
| Region | `regions/` | `id`, `level` (strength offset), `nationalities` (weighted mix) |
| Nationality | `nationalities/` | `id`, `code` (ISO 3166-1 alpha-2), `name_order` (`given_first` / `family_first`) |
| Name pool | `name-pools/` | `nationality`, `given`, `family` |
| Nickname pool | `nicknames/` | `nicknames`; every pool is merged into one |
| Competition | `competitions/` | `id`, `region`, `teams` |
| Team | `teams/` | `id`, `region`, `tag` (3 characters), `colours` (two hex colours), `reputation` (1–100) |
| Player (pinned) | `players/` | `id`, `team`, then any subset of the generated fields |
| Role set | `roles/` | roles in display order, each with its overall weights (see [attributes](attributes.md)); `subs` |
| Generator constants | `generation/` | see [world generation](world-generation.md) |

## Scenarios

### PKG-001 — The core package loads with no errors

- **Given** the `content/core` package in the repository
- **When** it is loaded and validated
- **Then** the report is empty, and the content has 2 regions, 2 competitions, 18 teams and 11 nationalities

### PKG-002 — A file can hold one entity or a list

- **Given** a package with `teams/a.json` holding one team and `teams/more.json` holding a list of two teams
- **When** it is loaded
- **Then** it has three teams

### PKG-003 — Subfolders and file names carry no meaning

- **Given** a package whose only player is in `players/kr/anything.json`, with id `player:kairos`
- **When** the file is moved to `players/kairos.json` and the package is loaded again
- **Then** the package loads, and it has the same player with id `player:kairos`

### PKG-004 — Duplicate ids are reported with both files

- **Given** a package where `teams/a.json` and `teams/b.json` both define `team:azure_tigers`
- **When** it is loaded
- **Then** the report has one duplicate-id error naming `team:azure_tigers`, `teams/a.json` and `teams/b.json`

### PKG-005 — An id's kind must match its folder

- **Given** a package with a file in `players/` that defines `team:azure_tigers`
- **When** it is loaded
- **Then** the report has a wrong-kind error for that file, expecting kind `player`

### PKG-006 — Unknown fields are errors, with their path

- **Given** a team file with the field `"reputaton": 80` at index 2 of its list
- **When** the package is loaded
- **Then** the report has an unknown-field error with that file and the path `[2].reputaton`

### PKG-007 — Unknown top-level folders are errors

- **Given** a package with a folder `team/` next to `teams/`
- **When** it is loaded
- **Then** the report has an unknown-folder error for `team/`

### PKG-008 — References must resolve

- **Given** a team whose `region` is `region:atlantis`, which no file defines
- **When** the package is loaded
- **Then** the report has an unresolved-reference error naming the team, the field `region` and `region:atlantis`

### PKG-009 — Every error is reported at once

- **Given** a package with a duplicate id, an unknown field and an unresolved reference in three different files
- **When** it is loaded
- **Then** the report has all three errors, in sorted file order

### PKG-010 — Translatable names must exist in the first locale

- **Given** a package declaring locales `en` and `pt-BR`, with a team whose `team-…` message is missing from `locales/en/`
- **When** it is loaded
- **Then** the report has a missing-text error naming the message id and the locale `en`

### PKG-011 — A name missing in another locale falls back

- **Given** a loaded package with a team's name in `en` only
- **When** the team's name is shown in `pt-BR`
- **Then** the English name is shown

### PKG-012 — A broken package produces no save

- **Given** a package with at least one validation error
- **When** a new game is started from it
- **Then** the result is the validation report, and no save file exists

### PKG-013 — `$schema` is accepted on single-object files

- **Given** a team file holding one object with a `$schema` field
- **When** the package is loaded
- **Then** it loads with no errors, and the team has no extra data

## Enforcement

These land with the code in the implementing PR:

- **Schema drift (ADR 0005):** CI regenerates `content/schemas/` and fails if the committed copies differ.
- **No rest patterns (ADR 0005):** the conversion module from package types to domain types destructures every type exhaustively. A CI script fails if a `..` rest pattern appears in it.
- **Core loads in CI:** PKG-001 is that check.
- **Core text parity:** the i18n gates in `tools/i18n/` cover only the UI catalogs today. They are extended to `content/core/locales/`, so core has every message in `en` and `pt-BR`.

## Open questions

- Override-by-id and load order across packages (with user packages).
- `.zip` packages and asset overrides (with user packages and art).
- Whether a pinned player can leave its role out and have the generator pick one of the team's missing roles.
