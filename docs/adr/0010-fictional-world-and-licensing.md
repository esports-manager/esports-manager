<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# 0010. Fictional world, licensing and assets

- **Status:** Accepted; how packages declare their licence is amended by [0011](0011-package-licence-in-the-manifest.md), and how files declare theirs by [0012](0012-licence-headers-in-every-file.md)
- **Date:** 2026-10-15
- **Related:** [0005](0005-esm-packages.md)

## Context

The Python implementation shipped real-world data: 171 League of Legends champions with Riot image URLs, 85 real professional players, 16 real teams, and real team logos and player photos. Those are third-party trademarks and copyrighted material, incompatible with a GPL project, and they contradict the project's own goal of a generic esport.

## Decision

- **The world is fictional.** The base game ships original champions, teams, players, staff, leagues and regions. The MOBA rules are our own (one map, three lanes plus jungle, five roles). We are free to simplify them, and must not copy a commercial game's names, abilities, art or league branding.
- **Real-world data is never distributed by this project.** Users may create such packages for personal use. That is their responsibility, and this repository does not host or link to them.
- **Licensing:** all code and the base-game content (data, `.ftl` text, generated art) are GPL-3.0-or-later. Third-party packages declare their own licence in their manifest.
- **The repository is REUSE-compliant.** `REUSE.toml` covers files we write. Any third-party file must carry its own licence declaration.
- **Art in the MVP is procedural:** deterministic geometric glyphs for champions, monogram crests for teams built from their colours, and silhouettes for people. Packages can override any of them with real art. That is also the first test of package asset overrides.
- **AI-generated art** is not used without a separate ADR settling its licensing.

## Alternatives considered

- **Shipping real data, or an official real-world package.** Legal risk for the project and its distributors.
- **Commissioning art now.** Premature before the game is playable.

## Consequences

- The Python seed data and assets are not carried over. They remain only in the `python-final` tag.
- We have to write a world: champion identities, team names, regions. The generator does most of the population work.

## Enforcement

- `reuse lint` runs in CI.
- Review checks content PRs for real-world names and branding. This can't be automated reliably, so it is a deliberate exception to ADR 0008.
