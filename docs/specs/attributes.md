<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Attributes and overall

- **Prefix:** `ATTR`
- **Status:** Implemented
- **Related:** [ADR 0002](../adr/0002-genre-seam.md), [condition](condition.md), [champions and mastery](champions-and-mastery.md), [world generation](world-generation.md), [roster](roster.md)

## Summary

Attributes describe what a person can do and who they are. Every attribute must have at least one documented consumer in the simulation or in the development model; an attribute that nothing reads doesn't exist. The Python implementation had 13 skills that mostly collapsed into one "overall", and this spec exists to prevent that.

## Scale

- Shown on a 1–99 scale. Stored in whole hundredths (1.00–99.00) so that small training gains accumulate without a visible jump every week. The stored value is an integer number of hundredths (`domain::Rating`); floats never reach the save.
- Three categories:
  - **skills:** trainable
  - **traits:** personality, slow to change
  - **hidden:** never shown raw; only estimated through scouting, with accuracy depending on staff

## Core attributes (`domain`, every genre)

| Attribute | Category | Consumed by |
|---|---|---|
| Teamwork | trait | Synergy accumulation, how well the player follows calls |
| Aggression | trait | How often fights are started, and the variance that brings. Neither good nor bad in itself |
| Composure | trait | Performance when behind or in high-stakes games, tilt resistance; the starting point of in-match composure |
| Work Ethic | trait | Training and solo-queue gains, tolerance of stamina costs |
| Consistency | hidden | How much performance varies from match to match |
| Potential | hidden | Ceiling of development |

## MOBA skills (`esports::moba`)

| Attribute | Consumed by |
|---|---|
| Mechanics | Execution in skirmishes and teamfights, outplay chance |
| Laning | CS rate, trades, lane pressure |
| Game Sense | Rotations, wave management, objective setup, jungle pathing |
| Awareness | Avoiding ganks and picks, vision use |
| Positioning | Survival and damage uptime in teamfights |
| Champion Pool Breadth | How fast new champions are learned, adaptation to patches |
| Shotcalling | Team coordination bonus when this player is the designated caller |

## Overall

- Overall is **for display and AI heuristics only**: squad screens, scouting, AI valuation of players. **The match simulation never reads it.**
- Read it like this: in the low 90s means elite; lower numbers mean weaker players.

### Which attributes count

**The seven MOBA skills plus Teamwork and Composure.** Three kinds of attribute are left out:

- **Aggression:** a style, neither good nor bad.
- **Work Ethic:** drives growth, not current ability.
- **Hidden attributes** (Consistency, Potential): a visible number would leak them.

### Formula

- overall = Σ(wᵢ × aᵢ) / Σwᵢ, over the counted attributes, with the weights of the player's **main role**.
- It is computed in integer hundredths and rounded to the nearest hundredth, ties away from zero.
- **Display:** the stored value is rounded to a whole number, ties away from zero, so 72.50 shows as 73.

### Ownership

- **`domain`:** `Rating` (hundredths, 1.00–99.00), display rounding, and the weighted mean over `(Rating, weight)` pairs. Domain doesn't know any role or skill names.
- **`esports::moba`:** the MOBA attributes, the role set, and `overall(player)`, which picks the main role's weights and calls the domain mean.
- **The weights live in exactly one place:** the role set in the package's `roles/`. The generator's role bias ([world generation](world-generation.md)) reads the same table, so what a role values is defined once.

### Role weight table

Integer weights; each role's column sums to 100.

| Attribute | Top | Jungle | Mid | Bot | Support |
|---|---|---|---|---|---|
| Mechanics | 16 | 14 | 20 | 20 | 10 |
| Laning | 18 | 6 | 16 | 18 | 12 |
| Game Sense | 14 | 20 | 14 | 10 | 14 |
| Awareness | 10 | 14 | 10 | 10 | 16 |
| Positioning | 12 | 8 | 12 | 16 | 12 |
| Champion Pool Breadth | 6 | 6 | 8 | 6 | 6 |
| Shotcalling | 4 | 14 | 6 | 4 | 14 |
| Teamwork | 10 | 10 | 6 | 8 | 10 |
| Composure | 10 | 8 | 8 | 8 | 6 |

### Validation (`packages`)

- Every role in the role set has a weight for every counted attribute.
- Weights are non-negative integers, and each role's weights sum to more than zero.

## Profile display

- **Skills and traits** show their whole-number value.
- **Hidden attributes** show as unknown, until scouting exists. Their values are never sent to the UI.

## Scenarios

### ATTR-001 — Overall is the role-weighted mean

- **Given** a mid with every counted attribute at 70.00 except Mechanics at 90.00
- **When** their overall is computed
- **Then** it is 74.00: (20 × 90 + 80 × 70) / 100

### ATTR-002 — Attributes outside the formula don't move overall

- **Given** a player whose overall is 74.00
- **When** their Aggression, Work Ethic, Consistency and Potential change
- **Then** their overall is still 74.00

### ATTR-003 — The main role picks the weights

- **Given** two players with identical attributes, one a mid and one a support
- **When** their overalls are computed
- **Then** each uses their own role's weights, and the two values differ if the weighted means differ

### ATTR-004 — Display rounds ties away from zero

- **Given** stored overalls of 72.49 and 72.50
- **When** they are displayed
- **Then** they show as 72 and 73

### ATTR-005 — Weights come from the package

- **Given** a package whose role weights give Mechanics a weight of 100 for mid and every other weight 0
- **When** a mid's overall is computed
- **Then** it equals their Mechanics

### ATTR-006 — Invalid weights are package errors

- **Given** a package where the support weights are all 0, and the jungle weights leave out Composure
- **When** it is loaded
- **Then** the report has a zero-sum error for support and a missing-weight error for jungle and Composure

### ATTR-007 — Hidden attributes never reach the profile

- **Given** a player with Consistency 25.00 and Potential 94.00
- **When** their profile view is built
- **Then** it lists both as unknown, and contains no value for either

## Open questions

- The development model: growth curves by age, potential and activity. This needs its own spec.
- Whether staff get their own attribute set (needed once staff arrive, after the MVP).
- Tuning the role weights once the match simulation exists, in sim-bench.
