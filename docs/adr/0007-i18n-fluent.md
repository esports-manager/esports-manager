<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# 0007. Internationalization with Project Fluent

- **Status:** Accepted
- **Date:** 2026-10-15
- **Related:** [0005](0005-esm-packages.md), [0006](0006-bindings-and-pure-view.md)

## Context

Openfoot Manager's backend sent English prose first and added keys later. The domain types ended up carrying both (`subject` + `subject_key`), old saves had to be regex-parsed, and errors were encoded as strings like `"key?amount=123"`. Its i18n audit script always exited 0, so production code got around it. The Python `i18n` branch hard-coded the locale at import time and never compiled its catalogs.

Generated match narration is the hardest i18n surface in this game. Portuguese needs grammatical gender ("o jogador abatido" / "a jogadora abatida") and plural rules that `str.format` templates can't express.

## Decision

- **Project Fluent (`.ftl`) is the one catalog format** for UI strings, narration, errors and package content.
  - The UI uses `@fluent/react`. Rust uses `fluent-rs` only where text must be rendered outside the UI: CLI output and narration tests.
- **The backend never produces prose for the UI.** It emits `(message id, typed arguments)`. Errors carry a code plus typed parameters. The frontend renders them.
- **Launch locales are `en` and `pt-BR`, both complete from the first feature.** A second real locale is what catches hard-coded strings, concatenation and plural bugs.
- **Narration** is a pure presenter: `match event → (message id, args)`. When there are several variants, one is chosen by a deterministic hash of the event, so a replay reads the same in every run.
- **Packages ship their own `.ftl` files** per locale. A package that adds a champion also adds its name in each locale it supports. The base game is no exception.
- The locale is a runtime setting with fallback to `en`.

## Alternatives considered

- **i18next JSON** (Openfoot Manager). Works for UI strings, but it would need a second system for Rust and narration, and its plural and gender handling is weaker than Fluent's.
- **gettext.** Weak tooling in the browser, and gender selection is awkward.

## Consequences

- Every user-visible string needs a message id.
- Translators work with `.ftl` files, which are plain text and diffable.

## Enforcement

- **Locale coverage test:** every locale has every message id defined in `en`, with the same arguments.
- **Key coverage test:** every message id referenced in TS or Rust exists in `en`, and every id in `en` is referenced somewhere (no dead strings).
- A check script (built on the TypeScript compiler API) fails on JSX text and string-literal props such as `title`, `aria-label` and `placeholder` outside the i18n layer.
- These tests fail the build. There is no advisory mode.
