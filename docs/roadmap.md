<!--
SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
SPDX-License-Identifier: GPL-3.0-or-later
License-Filename: LICENSES/GPL-3.0-or-later
-->

# eSports Manager roadmap

The game is being rewritten in Rust + Tauri + React/TypeScript. The Python implementation is preserved at the `python-final` tag. This roadmap will change as development goes on.

## Milestone 0: foundation

- Repository reset, ADRs, game design overview, draft specs.
- Rust workspace skeleton, toolchain, lints, `just check`, architecture test, coverage, mutation testing, CI.
- Desktop shell (Tauri) and frontend skeleton with generated bindings, Fluent (en + pt-BR), Vitest and Playwright.

## Walking skeleton

New Game → load the core package → generate a two-region world → write a SQLite save → show my roster and player profiles, in the CLI and the UI. Saves live in the OS data folder, or next to the executable in a portable build (Windows, Linux).

## 0.1.0: MVP

One MOBA split from New Game to the end-of-split evaluation. See [MVP scope](game-design/mvp.md).

## After the MVP (unordered, to be prioritized)

- Season rollover, contracts and transfers
- The solo-queue talent-discovery network and scouting knowledge
- Staff with attributes; streaming, VOD review and individual practice
- Patches (from packages and from a generated balance team) and a world-discovered meta rating
- Finances, sponsors and facilities; board firing
- More than two regions, and international competitions
- Schematic minimap in the match view
- World Editor
- MCP adapter for AI play-testing
- Android build
- Other genres: RTS, FPS
