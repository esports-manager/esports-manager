<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# 0005. `.esm` content packages

- **Status:** Accepted
- **Date:** 2026-10-15
- **Related:** [0004](0004-sqlite-and-diesel.md), [0007](0007-i18n-fluent.md), [0010](0010-fictional-world-and-licensing.md)

## Context

Modding is a first-class goal: users should be able to create their own worlds, with regions, leagues, competitions, teams, players and champions. Openfoot Manager had a package format (`.ofm`) whose schema was written by hand in four places (Rust structs, CLI, editor types, a reference document), so the copies drifted apart. Some fields were validated and then ignored.

## Decision

- **The `.esm` package** is a `.zip` file (or an unzipped directory during development) holding a `manifest.json` and JSON content files.
  - The manifest declares: id, version, title, licence, authors, genre, dependencies and load order.
- **What a package can define:**
  1. **Data:** regions, nationalities and name pools, leagues, competitions, teams, players, staff, champions, mastery tiers.
  2. **Rules as configuration:** role sets, draft order and ban counts, series formats, map objectives and timers, competition stages and qualification links, attribute role weights.
  3. **Text:** Fluent `.ftl` files per locale for the package's own content (champion names, team names, narration templates).
  4. **Assets:** icons, logos, portraits, overriding the procedural placeholders.
- **The base game is a package.** `content/core` is loaded through the same pipeline as any user package. If the base game can't be expressed as a package, the format is incomplete.
- **Stable string ids** (`champion:ember_witch`) identify content. Later packages can override or extend earlier ones by id. At load time, ids resolve to compact typed ids.
- **JSON Schemas are generated from the Rust types** (`schemars`). The schemas, the loader's validation and the World Editor all derive from the same types. There is no hand-written schema.
- **Validation reports are a product feature.** Loading a broken package produces a readable list of errors with file, path and reason, in the user's language.
- **Packages are compiled into a save at New Game** (ADR 0004). A pack defines structure; the deterministic generator fills in players and staff where the package doesn't pin them.
- **No code mods in v1.** Packages hold data, rules, text and assets, never scripts. New genres are added as Rust modules in this repository.
- **World Editor:** a mode inside the same app, after the MVP. It edits packages and reuses the loader's validation.

## Alternatives considered

- **TOML.** Pleasant to hand-edit, but editing it from a program loses comments and formatting, and the World Editor will be the main authoring tool.
- **RON.** Rust-native, unfamiliar to modders.
- **Scripting (Lua, Rhai, WASM).** Would allow behaviour mods, but costs a sandbox, a stable API surface and determinism guarantees. Not justified yet.
- **Packages as SQLite files.** Not diffable or reviewable in git.

## Consequences

- Every content type needs a Rust type with `serde` + `schemars` derives, and that type is the single definition.
- Modders get editor autocompletion and validation from the generated schemas.

## Enforcement

- CI regenerates the schemas and fails if the committed copies differ.
- The core package is loaded and validated in CI.
- The loader converts each package type into its domain type by **exhaustive destructuring** in one conversion module. Rest patterns (`let ChampionDef { id, name, .. } = def;`) are banned there, so every field must be bound: a new field the conversion doesn't bind is a compile error, and a bound field that is never used fails `-D unused_variables`. Together these rule out "validated then ignored". A CI script fails if a rest pattern appears in the conversion module.

## Revisit when

A concrete mod idea can't be expressed with data, rules, text and assets. That would reopen the question of code mods.
