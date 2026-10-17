<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# 0003. Deterministic simulation

- **Status:** Accepted
- **Date:** 2026-10-15
- **Related:** [0001](0001-clean-architecture-and-workspace-layout.md), [0004](0004-sqlite-and-diesel.md)

## Context

Every earlier implementation used unseeded randomness: Python's global `random`, a mix of `rand` and a custom RNG in `rewrite-rust`, and 65 `rand::rng()` calls in Openfoot Manager. Without determinism we can't take regression snapshots of match outcomes, replay a match, reproduce a bug from a save, or write precise property and mutation tests.

The game also lets the user make decisions while a match is running (focus changes) and between games of a series (talks, substitutions), so "deterministic" must hold with user input in the loop.

## Decision

1. **Same inputs, same outputs.** Given a save and its seed, advancing time always produces the same world.
2. **Named RNG streams.** A world has one seed. Every consumer derives its own stream from the seed and a stable label, for example `match:<id>`, `generator:season:<n>`, `scheduler:<date>`. We use a portable, versioned PRNG (ChaCha8 via `rand_chacha`). Adding a new consumer must not shift the sequence of any existing consumer.
3. **Domain code receives randomness; it never creates it.** Functions take `&mut impl Rng`. Only the `app` layer's RNG provider constructs streams.
4. **A match is a pure function** of `(initial match state, seed, decision log)`. The simulation advances in fixed ticks. A user decision is recorded as `(tick, decision)` and applies at the next tick boundary. A replay re-runs the same inputs. A match saved mid-way is stored as its inputs so far.
5. **Playback speed is presentation only.** The UI's watch speed never changes simulation timing.
6. **One match engine.** Official matches, scrims, AI-vs-AI matches and instant results all run the same engine; "instant" means running it with no viewer. There is no separate fast or Monte Carlo simulator.
7. **No wall-clock in the domain.** In-game time is `GameDate` plus slot. Real time exists only in adapters (autosave timestamps, logs).
8. **Deterministic iteration.** Collections whose order can affect results are ordered (`BTreeMap`, `IndexMap`, `Vec`), never `HashMap`/`HashSet`. Every database query that feeds a simulation has an explicit `ORDER BY`.

## Alternatives considered

- **A single shared RNG.** Rejected: any new consumer shifts every later draw, so every snapshot breaks with unrelated changes.
- **A separate quick-sim for AI matches.** Rejected: two engines drift apart, and duplicated logic is the failure we are designing against.

## Consequences

- Snapshot tests of whole matches and seasons are possible and expected.
- A bug report can be a save plus a version.
- Changing the PRNG algorithm or the stream labelling is a breaking save-format change and needs its own ADR.

## Enforcement

- `clippy.toml` `disallowed-methods` / `disallowed-types`: `rand::rng`, `rand::thread_rng`, `std::time::SystemTime::now`, `std::time::Instant::now`, `std::collections::HashMap`/`HashSet` are banned in `domain`, `esports` and `app`.
- Determinism tests run the same seed twice (fresh process state) and assert identical event streams.
- Repository methods in `db` that return collections must go through one ordered-query helper, which requires an ordering. Review checks that no repository method bypasses it. This can't be detected statically, so it is an explicit exception to ADR 0008.
