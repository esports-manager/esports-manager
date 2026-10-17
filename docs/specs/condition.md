<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Condition

- **Prefix:** `COND`
- **Status:** Draft
- **Related:** [ADR 0002](../adr/0002-genre-seam.md), [attributes](attributes.md)

## Summary

Condition is a person's current physical and mental state. It changes day to day through activities, matches, talks and results. It belongs to the genre-agnostic core (`domain`): every genre consumes condition and produces changes to it through the same interface, and no genre defines its own fatigue or morale.

## Rules (draft)

| Value | Range | Meaning | Main producers | Main consumers |
|---|---|---|---|---|
| Stamina | 0–100 | Physical and mental energy available today | Activities (cost), rest and overnight recovery (gain) | Match and activity performance; morale drain when low |
| Morale | 0–100 | How the person feels about the team and their situation | Results, talks, playing time, board and news events | Performance, development speed, willingness to stay |
| Form | 0–100 | Recent performance trend | Rolling window of recent match and scrim ratings | Performance variance, AI selection heuristics |
| Composure (state) | 0–100 | In-match tilt meter; starts each game from the Composure trait | In-match events (deaths, lost objectives), tactical calls, between-games talks | Decision quality during the match |

- Activities declare their effects in data (package rules): stamina cost per slot, morale effect, and genre-specific gains.
- The core trait **Work Ethic** changes stamina costs and training gains.
- Recovery happens when the day ends. The exact recovery formula is still open.
- Low stamina gives a performance penalty, which the genre's simulation reads through one accessor. Genres never read the raw number and apply their own curve.

## Open questions

- The recovery curve, and whether rest days recover more than an empty slot.
- Is form a stored value or derived from match history at query time? This is a single-source-of-truth question; deriving it is preferred.
- How visible is composure to the user during a match?
