<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# 0008. Enforcement policy and quality gates

- **Status:** Accepted
- **Date:** 2026-10-15
- **Related:** all ADRs; [CONTRIBUTING.md](../../CONTRIBUTING.md)

## Context

In Openfoot Manager the advisory checks didn't hold:

- an i18n audit that always exited 0
- a deduplication reviewer that was "not a gate"
- a "do not add readers" comment that gained 11 readers

A quality-ratchet file did gate, but every PR had to edit it, so concurrent merges broke `develop`.

The project is written with AI agents and humans together, and must stay maintainable by humans alone.

## Decision

**A rule only counts if a compiler, a lint or a failing CI check enforces it.** When a rule proves too strict in practice, we relax it in a reviewed change, rather than leaving it unenforced.

**One command, the same everywhere.** `just check` runs every gate. Humans run it locally and CI runs the same recipe. `lefthook` runs a fast subset (formatting, Biome, bindings drift) as a pre-commit hook.

**Rust gates:**

- Toolchain pinned in `rust-toolchain.toml`, edition 2024, `--locked` on every cargo invocation in CI.
- `cargo fmt --check`.
- `clippy` with `-D warnings` and workspace lints:
  - `clippy::pedantic` denied, with a short allow-list where each entry has a comment saying why
  - `clippy::unwrap_used`, `expect_used` and `panic` denied outside tests
  - `clippy::wildcard_enum_match_arm` denied
  - `unsafe_code = "forbid"`
- `disallowed-methods` and `disallowed-types` from ADR 0003.
- Errors: `thiserror` enums per crate; application errors carry a message id plus typed params. `anyhow` only in binary `main`s.
- `cargo-deny` (licences, bans, sources; advisories on a weekly schedule) and `cargo-machete`.
- The architecture test (ADR 0001).
- **Line coverage** via `cargo-llvm-cov`, per crate:

  | Crates | Minimum |
  |---|---|
  | `domain`, `esports`, `app` | 90% |
  | `packages`, `db` | 80% |
  | `cli`, `src-tauri` | 60% |

- **Mutation testing** with `cargo-mutants --in-diff` on every PR. A surviving mutant fails the PR unless it is marked as equivalent with a written reason. A full run happens every week.

**Frontend gates:** TypeScript strict, Biome, knip at zero, Vitest (80% line coverage on `src/lib` and hooks), Playwright at desktop and compact viewports with `axe`, Stryker weekly on the same scope, bindings drift (ADR 0006), locale coverage (ADR 0007).

**Cross-cutting gates:**

- Spec-to-test traceability (ADR 0009)
- `reuse lint` (ADR 0010)
- Conventional Commits on PR titles
- Generated JSON Schemas up to date (ADR 0005)
- Sim-bench statistical envelopes on PRs that touch the simulation, with a larger run nightly

**CI layout:** every PR runs all gates on Linux, including a `tauri-driver` smoke test of the real binary. Merges to `develop` also build on Windows and macOS. macOS builds are unsigned until a signing key is available. A nightly job runs the large sim-bench; a weekly job runs full mutation testing and `cargo-deny` advisories.

**Human-first documentation.** `CONTRIBUTING.md` and `docs/` are the single source of truth for conventions. `CLAUDE.md` and `AGENTS.md` are thin indexes into them and must not be the only place a rule is written. Project skills for agents are added only after a pattern has repeated three times, and are never required to make a change correctly.

## Alternatives considered

- **Advisory reports with a ratchet file.** Tried in Openfoot Manager; concurrent PRs conflict on the ratchet.
- **No coverage thresholds.** Coverage alone doesn't prove tests are meaningful. That is why mutation testing is a gate too.

## Consequences

- PRs take longer to get green. That is intended.
- Thresholds are expected to be tuned after the first month of real code.

## Enforcement

This ADR is enforced by the CI workflows and the `justfile`. Removing or weakening a gate requires a PR that changes this ADR, or a new ADR.
