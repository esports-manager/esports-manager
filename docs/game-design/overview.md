<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Game design overview

This document is the shared understanding of what eSports Manager is. It was agreed in the October 2026 design sessions that started the Rust rewrite. Detailed rules live in [specs](../specs/README.md), structural decisions in [ADRs](../adr/README.md).

## The game

eSports Manager is a free and open-source, single-player management game in the tradition of Football Manager and Bygfoot. You run a professional esports team: you build the roster, plan the practice schedule, prepare and call drafts, develop players, and guide the team through its competitions.

- **Genre:** MOBA first. The core is genre-agnostic so other MOBAs, RTS (StarCraft II-like, Age of Empires-like) and FPS (Counter-Strike-like) can follow ([ADR 0002](../adr/0002-genre-seam.md)). A save holds one genre.
- **The world is fictional**, with original champions, teams and players ([ADR 0010](../adr/0010-fictional-world-and-licensing.md)).
- **Modding is first-class.** The base game is itself a content package, and users can build entire worlds: regions, leagues, competitions, teams, players, champions and rules ([ADR 0005](../adr/0005-esm-packages.md)).
- **Platforms:** Linux, Windows and macOS desktop. Android later, so every screen also gets a compact layout.
- **Languages:** English and Brazilian Portuguese from the first feature.

## Who you are

You are the team's **head coach and general manager**. You handle the roster, contracts, scouting, staff, the schedule, scrims, lineups, drafts and player talks. An AI **board** sets season objectives and evaluates you against them. Sponsors and facilities, when they arrive, are board-level systems you influence rather than control.

## Time

- The calendar advances **day by day**. "Continue" moves to the next thing that needs you; the inbox can interrupt.
- Each day has **three slots**: morning, afternoon and night. A day can hold several activities, for example two scrims and a solo-queue session.
- **Activities** compete for players' **stamina**. Stamina management is part of the game. Activities, by milestone:
  - **MVP:** scrims, solo queue (optionally focused on learning a champion), rest.
  - **Later:** streaming, VOD review, individual practice.
- **Scheduling:** you plan scrims weekly or monthly. Scrims are requests to other teams. AI teams keep their own schedules, but your requests are resolved first, and AI teams avoid clashing with them.
- **Scrims are full games.** You can watch them, take part in the draft, or just get the result.
- **Delegation:** each responsibility can be set to *Me*, *Assistant*, or *Assistant, but ask me first*. The assistant coach uses the same AI code that runs AI teams.

## People

- **Attributes** use a 1–99 scale. Finer progress is kept internally so small gains accumulate. Attributes are in three groups:
  - **skills** (trainable)
  - **traits** (personality, slow to change)
  - **hidden** (only estimated through scouting)
- **Overall** is a role-weighted summary meant only for display: a 92 tells you at a glance that the player is elite. The simulation never reads it.
- **Condition** (stamina, morale, form, composure) belongs to the genre-agnostic core and is shared by every genre. See the [attributes spec](../specs/attributes.md) and the [condition spec](../specs/condition.md).
- A **generator** creates players and staff for any purpose: populating a new world, renewing it over the years, and bringing new talent through solo queue. It is deterministic, driven by name pools per nationality.

## Champions and mastery

- Each champion has a role suitability per role, class tags, a **power curve** (early/mid/late strength), a damage profile, and a capability profile (engage, poke, crowd control, waveclear and so on).
- Team compositions are classified into archetypes. Matchups are derived from capability profiles, with optional overrides in data.
- Champions have a derived **overall** for display, and a meta rating that the world discovers from its own match results (after the MVP).
- **Patches** change champion numbers. They come from packages and from a generated in-world balance team, and arrive after the MVP. Champion stats are always read through the current patch.
- **Mastery** per player and champion grows with games played and decays slowly when a champion isn't played. Its tiers are **Novice → Practiced → Proficient → Expert → Master → Signature**. Tiers give **bonuses only**; an unfamiliar champion is not penalized. Learning is faster for champions similar to ones the player already knows.

See the [champions and mastery spec](../specs/champions-and-mastery.md).

## Matches

- **The simulation is state-driven on an abstract map.** Players have positions in zones, gold, experience and alive/dead state. Situations such as trades, ganks, objective setups and teamfights arise from that state and are resolved by attribute contests.
  - There are no hard-coded game phases. The feel of early, mid and late game comes from champion power curves, objective timers and gold.
- **Before the match** you set a game plan: stance, objective priority and focus lane. **During the match** you can adjust the focus a limited number of times. Real coaches can't talk to players mid-game; we deliberately allow this.
- **Between games of a series:** player talks, substitutions, side selection and draft preparation. Series rules such as Fearless draft belong to each competition.
- **Watch modes:** full play-by-play, highlights, or instant result.
  - **MVP view:** text commentary, scoreboard and gold graph.
  - **Next:** a schematic minimap.
- **One match engine** runs everything, deterministically ([ADR 0003](../adr/0003-deterministic-simulation.md)).
- **Knowledge:** you and the AI see opponents only through what is knowable (match history, later scouting and scrims). Hidden attributes are only ever estimated. One knowledge model serves both the user and the AI.
- **Draft AI:** scores candidate champions on patch strength, mastery, composition synergy, counters, flex value and denial. It is deterministic; its difficulty comes from noise and lookahead.

The detailed simulation design is its own spec, written after the walking skeleton.

## Competitions

Competitions are composed from data, so users can build any league or tournament:

- **Stages:** round robin, Swiss, single or double elimination, groups.
- Each stage sets its **series format, tiebreakers and draft rules**.
- **Qualification links** connect stages and competitions.
- **Editions** snapshot the rules for each season, so a league can change its format next season.

See the [competitions spec](../specs/competitions.md).

## Out of scope for now

Code mods, multi-genre organizations, multiplayer and real-world data.
