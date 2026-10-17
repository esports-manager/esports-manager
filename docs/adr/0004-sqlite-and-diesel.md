<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# 0004. SQLite as the source of truth, accessed through Diesel

- **Status:** Accepted
- **Date:** 2026-10-15
- **Related:** [0001](0001-clean-architecture-and-workspace-layout.md), [0003](0003-deterministic-simulation.md), [0005](0005-esm-packages.md)

## Context

A save must hold a world that grows without bound: seasons of match logs, statistics, transfers and news. Users will build their own worlds. Two past mistakes guide the design:

- Openfoot Manager kept the whole world in memory and wrote it with hand-written positional SQL, so adding one field meant five edits per repository plus a migration. Enums were stored with `format!("{:?}")` and read back through a `match` ending in `_ =>`. A whole-world `Mutex` had no rollback on error.
- `rewrite-rust` stored JSON blobs inside SQLite columns, defeating the relational schema.

## Decision

- **Each save is one SQLite file, and it is the source of truth at all times.** Use cases read and write through repository ports; there is no in-memory copy of the world to keep in sync.
- **Each time advance is one transaction.** If anything fails while processing a day, the whole day rolls back.
- The match simulation loads the aggregates it needs, runs purely in memory (ADR 0003), and writes its results back in the same transaction.
- **Access goes through Diesel** (synchronous, compile-time checked queries, `schema.rs` generated from migrations). Diesel appears only in the `db` crate.
- **Migrations are versioned and tested.** Every migration has a test that opens a fixture save from the previous version, migrates it, and checks it.
- **Enums map through one `ToSql`/`FromSql` implementation per type**, with exhaustive matches and `CHECK` constraints. No catch-all arms.
- **No JSON-in-columns** for domain data. Structured data gets tables.
- SQLite is bundled (`libsqlite3-sys` with the `bundled` feature) so builds behave the same on Linux, Windows, macOS and later Android.
- New games are created by compiling one or more `.esm` packages into a fresh save (ADR 0005). Packages are templates; the save is the world from then on.

## Alternatives considered

- **An in-memory world aggregate with serde snapshots.** Simpler to start, but history grows without bound, and it reintroduces a second representation of the world to keep in sync.
- **sqlx.** Async-first (the domain and use cases are synchronous), and compile-time checking needs a committed offline query cache.
- **SeaORM.** Async, and a heavier abstraction than we need.
- **rusqlite with hand-written SQL.** The Openfoot Manager pain point.

## Consequences

- Adding a field means a migration plus a struct field, and sometimes a mapping.
- Screen queries can be written as efficient SQL instead of scanning the world.
- Saves and the future World Editor share one format.

## Enforcement

- The architecture test (ADR 0001) bans `diesel` outside `db`.
- `clippy::wildcard_enum_match_arm` is denied workspace-wide.
- Migration fixture tests run in CI.
- The ordered-query helper from ADR 0003.
