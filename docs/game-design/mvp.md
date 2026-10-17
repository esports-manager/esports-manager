<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# MVP scope (0.1.0)

The MVP is the smallest thing that is a game: one MOBA split, played from New Game to the end-of-split evaluation.

## In scope

- **New Game:** enter a manager name, pick a team in either of **two regions, each with one league** (10 and 8 teams in the core world). The world is built from the core package plus the generator. Starting with two regions keeps "the user's league" from being hard-coded anywhere, which Openfoot Manager found costly to undo later.
- **One split in each league:** a round-robin regular season, then a playoff bracket, with one qualification link from the regular season to the playoffs. The other league's matches run on the same engine in instant mode.
- **Roster and people:** roster view, player profiles, attributes, condition, champion pools and mastery tiers.
- **Calendar:** day by day with three slots per day, plus an inbox that can block "Continue" until it is handled.
- **Activities:**
  - **scrims** booked with AI teams, which you can watch, draft or simulate
  - **solo queue**, with an optional champion focus
  - **rest**
  - a weekly or monthly schedule, with per-player overrides
  - stamina as a real resource
- **Assistant coach** with delegation settings (*Me* / *Assistant* / *Ask me first*), using the same AI as the AI teams.
- **Match day:**
  - set the lineup
  - draft against the AI (pick/ban)
  - set a pre-game plan
  - watch in full, highlights or instant mode, with limited live focus calls
  - between-games talks, substitutions and side selection in a series
  - a post-match stats screen
- **Match view:** text commentary, scoreboard, gold graph.
- **Board:** a season objective, and an evaluation when the split ends. No firing.
- **End of the MVP loop:** a split summary, after which the game ends.
- **Save and load.** Autosave happens when a day advances.
- **Languages:** English and Brazilian Portuguese.
- **Art:** procedural placeholders.

## Out of scope

Transfers and contract negotiation, finances, staff beyond a fixed-competence assistant, the solo-queue talent-discovery network, streaming, VOD review, patches, more than two regions, international events, season rollover, the World Editor, the minimap, MCP play-testing, Android.

## Milestones toward it

1. **Milestone 0, foundation:** the repository, tooling, CI, ADRs and draft specs.
2. **Walking skeleton:** New Game → load core package → generate world → write SQLite save → show my roster and player profiles, in both the CLI and the UI. Specs: [packages](../specs/packages.md), [world generation](../specs/world-generation.md), [attributes](../specs/attributes.md), [saves](../specs/saves.md), [new game](../specs/new-game.md), [roster](../specs/roster.md); content: [core world](core-world.md).
3. **Match simulation design** (a dedicated session, prototyped in sim-bench), then the vertical features above, one spec at a time.
