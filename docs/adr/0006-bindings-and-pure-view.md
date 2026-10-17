<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# 0006. Generated bindings; the frontend is a pure view

- **Status:** Accepted
- **Date:** 2026-10-15
- **Related:** [0001](0001-clean-architecture-and-workspace-layout.md), [0007](0007-i18n-fluent.md)

## Context

Openfoot Manager's duplication audit traced several real bugs to the boundary between Rust and TypeScript:

- TS types were written by hand: a 791-line `types.ts`, plus `Backend*` interfaces and mappers.
- Finance rules were reimplemented in TS with different inputs, producing a false "finance crisis" alert.
- The frontend derived session state on its own, so the season could never roll over (#562).
- 51 commands returned the whole `Game`, the store held about 9,700 players, and the live match payload was 3.4 MB per tick.

## Decision

- **TypeScript types and the command client are generated from Rust** with `specta` + `tauri-specta`. Nobody writes an `invoke` call or a DTO interface by hand.
  - The first frontend PR runs a spike to confirm `tauri-specta` works with the pinned Tauri version. If it doesn't, we fall back to `ts-rs` for types plus a generated command map, and record that in a superseding ADR.
- **Rust owns every rule.** Every game rule, derived number, validation and decision lives in Rust. The frontend renders.
- **Each screen calls a dedicated query** (`get_roster_view(team_id) -> RosterView`) that returns exactly what that screen shows, already derived. No command returns the whole world.
- **The frontend may only localize:** translate message ids (ADR 0007) and format numbers, dates and money through `Intl`.
- **Frontend data layer:** TanStack Query wraps the generated commands. Each query is cached and invalidated by use-case results. There is no global world store; Zustand (or plain React state) is only for UI preferences.
- **Frontend stack:**
  - React 19, Vite, TypeScript in strict mode, TanStack Router, Tailwind v4 driven by design tokens.
  - An owned component kit built on Radix primitives.
  - pnpm; Biome for lint and format; knip.
- **Layouts:** desktop-first information density, but every screen has a specified compact layout from the start (no hover-only affordances, touch targets of at least 44px, a defined fallback for every table) so an Android build is possible later.
- **Accessibility baseline:** everything is keyboard-navigable, colour tokens meet WCAG AA contrast, and Playwright runs `axe` checks.

## Alternatives considered

- **Hand-written types with parity tests** (Openfoot Manager). The tests catch drift after the fact; generation prevents it.
- **`ts-rs` only.** Types without a command client, so `invoke` wrappers would still be hand-written. Kept as the fallback.

## Consequences

- Adding a backend field makes it appear in TS automatically; renaming one breaks the TS build at compile time.
- Screens may need new queries more often. That is intended: queries are cheap, duplicated rules are not.

## Enforcement

- CI regenerates the bindings and fails if the committed bindings differ.
- Biome and lint rules forbid direct `@tauri-apps/api` `invoke` imports outside the generated client.
- knip must report zero unused exports.
- Review rejects domain arithmetic in `src/`. A frontend lint rule for this is added if it shows up in practice.
