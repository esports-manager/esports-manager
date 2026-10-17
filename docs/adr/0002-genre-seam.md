<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# 0002. Genre seam: genre-agnostic core, one genre per save

- **Status:** Accepted
- **Date:** 2026-10-15
- **Related:** [0001](0001-clean-architecture-and-workspace-layout.md), [game design overview](../game-design/overview.md)

## Context

The game starts with MOBA (League of Legends-like). Other MOBAs (Dota-, HoN-, HotS-like), RTS (StarCraft II, Age of Empires) and FPS (Counter-Strike) are possible later. Building every genre now delays the MVP. Letting MOBA concepts leak into everything makes the second genre a rewrite.

## Decision

- **The core (`domain`) is genre-agnostic.** It owns everything any esport shares: people, the condition model (stamina, morale, form), core traits (Teamwork, Aggression, Composure, Work Ethic, Consistency, Potential), contracts, the calendar and day slots, competitions, the inbox, the knowledge model, money and dates.
- **Genre modules live in `esports`** (`esports::moba`). A genre defines its roster shape, gameplay skills, genre content (champions), pre-match flow (draft), match simulation, AI, and how its activities affect people.
- **Variants of a genre are data, not code.** A Dota-like MOBA is a different content package (roles, draft order, map objectives), not a new module.
- **One genre per world.** A save holds exactly one genre. The schema keeps genre-specific data in genre tables keyed by core ids, so multi-genre organizations are not ruled out, but they are not designed for.
- The `app` layer dispatches by the world's genre through an enum with one variant (`Genre::Moba`). There is no plugin registry.
- RTS and FPS are not implemented. Their only role now is as a check in design review: "would this seam allow a 1v1 RTS or a 5v5 FPS?"

## Alternatives considered

- **MOBA-only, generalize later.** Rejected: retrofitting a seam after the code depends on MOBA types costs more than drawing it now.
- **A plugin trait with dynamic registration, proven with a toy second genre.** Rejected as premature; it would slow the MVP for a benefit we can't measure yet.
- **Multi-genre organizations now.** Rejected: shared budgets and parallel calendars across divisions are a whole layer of design that the MVP doesn't need.

## Consequences

- MOBA-specific words (champion, lane, dragon, draft) must not appear in `domain`.
- When a concept seems shared, it goes into `domain` only once it is genre-neutral in shape, not just in name.

## Enforcement

- The architecture test (ADR 0001) fails if `domain` depends on `esports`.
- A CI check scans `crates/domain` for a deny-list of MOBA vocabulary.

## Revisit when

Work on a second genre starts, or a feature requires one organization to field teams in two genres.
