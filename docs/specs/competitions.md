<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Competitions

- **Prefix:** `COMP`
- **Status:** Draft
- **Related:** [ADR 0005](../adr/0005-esm-packages.md), [game design overview](../game-design/overview.md)

## Summary

Users must be able to build any region, league or tournament as data. Competitions are therefore **composed** from a small set of building blocks rather than coded per format. Formats coded one by one get reimplemented N times; this spec exists to avoid that.

## Model (draft)

- **Competition:** an identity (id, name, region, tier) plus an ordered list of stages. Competitions belong to the genre-agnostic core (`domain`).
- **Stage:** one of
  - round robin (single or double)
  - Swiss
  - single elimination
  - double elimination
  - groups (GSL or round robin within each group)

  Each stage sets:
  - its **series format**, which can differ by round (Bo1, Bo3, Bo5)
  - its **tiebreakers**, as an ordered list
  - its **genre rules**, such as draft rules. Fearless draft is an example: a rule option of the edition, not hard-coded.
- **Qualification link:** takes teams from one stage and seeds them into another stage or competition. Examples:
  - "Top 6 of the regular season → playoffs, seeds 1–6"
  - "League winner → international event, slot 1"
- **Edition:** one season's instance of a competition. Its rules are a snapshot taken when the edition is created, so a format change applies from the next edition and history stays accurate.
- **Calendar integration:** an edition generates its match days into the calendar, the single source of truth for when things happen.

## MVP subset

Round robin, single elimination, and one link between them (regular season → playoffs). The data shape is still the full composable model.

## Open questions

- Whether side selection (for example, the loser picks side) is a series rule or a draft rule.
- Scheduling constraints: matches per week, which days and slots they use.
- How tiebreakers referring to head-to-head results work across Bo1 and Bo3 stages.
