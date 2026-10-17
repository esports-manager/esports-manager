<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# 0011. A package's licence is declared in its manifest

- **Status:** Accepted
- **Date:** 2026-10-16
- **Related:** [0005](0005-esm-packages.md), [0010](0010-fictional-world-and-licensing.md), [packages spec](../specs/packages.md)

## Context

ADR 0010 says third-party packages declare their licence in their manifest, and also that "any third-party file must carry its own licence declaration". The packages spec makes a package's layout strict: only `manifest.json`, `world.json` and the content-type folders are allowed at the root, so a typo is reported instead of ignored. A `LICENSE` file or a REUSE sidecar (`*.license`, `REUSE.toml`) at the root is therefore an error. The two rules can't both hold for a package.

## Decision

- **A package's licence is the SPDX expression in its manifest's `license` field.** That is its licence declaration for ADR 0010; it covers every file in the package.
- **A package holds no licence files of its own.** The loader keeps rejecting unknown files at the root, `LICENSE` and REUSE sidecars included.
- **Inside this repository**, packages are covered by `REUSE.toml` like every other file (`content/core` is GPL-3.0-or-later). A third-party package added here gets its own annotation in `REUSE.toml`, matching its manifest.
- This amends only ADR 0010's rule on third-party files for packages. The rest of ADR 0010 stands.

## Alternatives considered

- **Allowing `LICENSE*`, `REUSE.toml` and `*.license` at a package's root.** It would loosen the strict layout for files the loader then ignores, and a package could declare one licence in its manifest and another in a file. One place is easier to check and to show in the UI.

## Consequences

- Licence texts aren't shipped inside packages; the SPDX identifier names them. A package author who needs to ship a notice puts it in the package's own distribution, outside the package folder.
- The UI and the saves can show and record a package's licence from the manifest alone.

## Enforcement

- The loader rejects unknown root files (`UnexpectedFile`) and requires a manifest `license` in SPDX form; both are tested in `crates/packages`.
- `reuse lint` runs in CI and checks that every file in the repository, packages included, is covered.
