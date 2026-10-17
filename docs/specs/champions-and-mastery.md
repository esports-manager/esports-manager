<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Champions and mastery

- **Prefixes:** `CHAMP`, `MAST`
- **Status:** Draft
- **Related:** [ADR 0005](../adr/0005-esm-packages.md), [attributes](attributes.md)

## Summary

Champions are a MOBA genre's content (`esports::moba`). Each one has a numeric identity that the simulation and the draft AI read. Mastery measures how well a player knows a champion, and is what makes champion pools, comfort picks and "learning a new champion" mean something.

## Champion model (draft)

- **Identity:** stable id, a name from Fluent, class tags (for example assassin, mage, tank, marksman, support, fighter).
- **Role suitability:** a value from 0 to 1 for each role in the package's role set.
- **Power curve:** strength in the early, mid and late game. This is where the feel of game phases comes from; the simulation has no hard-coded phases.
- **Damage profile:** the physical/magic split.
- **Capability profile:** engage, disengage, poke, burst, sustained damage, tankiness, crowd control, mobility, waveclear, split-push, objective damage, peel and utility.
- **Patch layer:** champion numbers are always read through the current patch, even while only one patch exists (MVP). Patches are data diffs over these numbers, after the MVP.
- **Overall:** derived from the capability profile and the patch modifiers, shown as 1–99 plus a tier letter. It is for display only; the simulation doesn't read it. After the MVP, a **meta rating** derived from the world's own pick, ban and win rates is added on top.

## Composition and matchups (draft)

- A team composition is the sum of its five capability profiles. It is classified into archetypes (engage, poke, split-push, protect-the-carry, pick) and gets a synergy score.
- Matchups are **derived** from the profiles: mobility against crowd control, poke against sustain, power-curve timing. Packages can add explicit counter overrides. There is no N×N counter matrix to maintain.

## Mastery (draft)

- Each player has hidden **mastery points** for each champion. They grow with games played (solo queue, scrims, official matches) and decay slowly when the champion goes unplayed.
- **Tiers:** Novice → Practiced → Proficient → Expert → Master → Signature. The tier names, point thresholds and bonuses are package data.
- **Bonuses only.** Each tier above Novice gives a bonus to the player's effective skills on that champion. Not knowing a champion is not penalized.
- **Hysteresis:** a player drops to a lower tier only once their points are a margin below its threshold, so a tier doesn't flicker back and forth.
- **Learning speed** depends on Champion Pool Breadth, Work Ethic, and how similar the champion is to ones the player already masters (shared class tags or role).
- "Learn this champion" is scheduled as a solo-queue activity with a champion focus.

## Open questions

- The capability dimensions: are 13 too many for modders to fill in? Should some be derived from class tags by default?
- Tier thresholds and bonus sizes. These get tuned in sim-bench.
- The decay rate, and whether Signature champions decay at all.
- The number of champions in the core package (somewhere in the 40–60 range for the MVP?).
