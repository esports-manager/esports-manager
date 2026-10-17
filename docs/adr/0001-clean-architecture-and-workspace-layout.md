<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# 0001. Clean Architecture and workspace layout

- **Status:** Accepted
- **Date:** 2026-10-15
- **Related:** [0002](0002-genre-seam.md), [0004](0004-sqlite-and-diesel.md), [0006](0006-bindings-and-pure-view.md)

## Context

eSports Manager is being rewritten from Python into Rust + Tauri + React/TypeScript. Two earlier attempts on the same stack show the failure modes to design against:

- `rewrite-rust` (2026) put business logic in Tauri commands (an 845-line `commands/core.rs`), let crate dependencies drift from the documented graph, and kept parallel duplicates (`Player`/`MobaPlayer`, two match sims, two draft AIs).
- Openfoot Manager (same author, same stack) grew a god struct, let the frontend recompute backend rules, and had a persistence crate depending on the game-logic crate.

We want clear seams, so each part can be tested on its own and replaced without touching the others.

## Decision

The codebase follows Clean Architecture: dependencies point inward, toward the domain.

```
crates/
  domain     Genre-agnostic core: ids, GameDate, Money, people, condition,
             contracts, calendar and slots, competitions, inbox, knowledge.
             Pure Rust. No IO, no wall-clock, no global RNG.
  esports    Genre modules. `esports::moba` now; `rts`, `fps` later.
             Attributes, champions, draft rules, match simulation, AI.
             → domain
  app        Application layer: use cases (commands and queries), ports
             (repository traits, package source, RNG provider), view DTOs.
             → domain, esports
  packages   Loads and validates `.esm` content packages; generates JSON
             schemas.  → domain, esports, app
  db         SQLite adapter (Diesel) implementing the repository ports.
             → domain, esports, app
  cli        Headless adapter: play, script and benchmark the game,
             including sim-bench.  → app, packages, db
src-tauri/   Desktop adapter. Thin Tauri commands that call use cases.
             → app, packages, db
src/         React/TypeScript UI.
content/core The base game, as an `.esm` package (ADR 0005).
```

Rules:

1. `domain` and `esports` must not depend on any IO, framework, database or UI crate.
2. Use cases live in `app` and nowhere else. Adapters (`cli`, `src-tauri`, a future MCP server) translate input, call one use case and translate the output. An adapter must not contain game rules.
3. Diesel types never leave `db`. The domain never sees a row struct.
4. Each concept has exactly one home. If two crates need it, it moves down to the lowest crate both depend on; it is never copied.
5. Two adapters (CLI and desktop) exist from the start so the use-case boundary is exercised by more than one caller. An MCP adapter for AI play-testing comes after the MVP loop and must call use cases only.

## Alternatives considered

- **A single crate with modules.** Cheaper to start, but module boundaries are not enforced by the compiler, and the earlier attempt showed that undocumented boundaries erode.
- **One crate per genre** (`moba`, `rts`, ...). Rejected for now: one `esports` crate with modules is simpler to maintain. It can be split if compile times demand it.

## Consequences

- Domain and genre code can be tested without a database or a UI.
- Every feature touches several crates (domain type, use case, adapter, UI). That is the price of the seams.
- The CLI must be kept working; it is the backbone of backend end-to-end tests and the sim benchmark.

## Enforcement

- An architecture test reads `cargo metadata` and fails if any crate depends on a workspace crate outside the arrows above, or if `domain`/`esports` depend on banned external crates (`diesel`, `tauri`, `rusqlite`, `tokio`).
- Lints ban wall-clock and unseeded RNG calls outside adapter crates (ADR 0003).
- Rule 2 and rule 4 are checked in review. Duplicated logic found later is a bug, fixed by moving it to its single home.
