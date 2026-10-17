<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# 0012. Every file that can hold a comment carries its licence header

- **Status:** Accepted
- **Date:** 2026-10-16
- **Related:** [0008](0008-enforcement-policy.md), [0010](0010-fictional-world-and-licensing.md), [0011](0011-package-licence-in-the-manifest.md)

## Context

ADR 0010 made the repository REUSE-compliant through `REUSE.toml`: one annotation, `path = "**"`, declared every file GPL-3.0-or-later. `reuse lint` passed, but only 9 of about 300 files said anything about their licence themselves. Two problems follow:

- A file copied out of the repository, or read on its own, doesn't say whose it is or under what terms.
- The catch-all also covers a third-party file that someone forgets to annotate. It is silently declared GPL-3.0-or-later, and the gate can't notice, because every file is always covered.

## Decision

- **Every file that can hold a comment must start with an SPDX header:** `SPDX-FileCopyrightText` and `SPDX-License-Identifier`, in the file's own comment syntax. That covers Rust, TypeScript, CSS, Markdown, Fluent, SQL, TOML, YAML, HTML, XML and SVG, and dotfiles such as `.gitignore`.
- **`REUSE.toml` annotates only files that can't carry a header:**
  - JSON (tool configuration, test fixtures, the generated package schemas)
  - binary files (icons, the test save)
  - lock files and generated files whose generator would drop a header (`Cargo.lock`, `pnpm-lock.yaml`, `crates/db/src/schema.rs`)
  - content packages, whose licence is their manifest's `license` (ADR 0011). A package in the repository gets one annotation that matches its manifest, so package files carry no headers.
- **The catch-all `**` annotation is removed.** A file with neither a header nor an annotation fails `reuse lint`.
- **Generated files carry a header when their generator can write one.** `src/bindings.ts` gets its header from the bindings exporter.
- **A third-party file keeps its own author and licence** in its header or its annotation, as ADR 0010 already requires.
- This amends ADR 0010's rule that "`REUSE.toml` covers files we write". The rest of ADR 0010, and ADR 0011, stand.

## Alternatives considered

- **Keeping the catch-all.** It is compliant, but it can't catch a missing declaration, which is the one mistake the check exists for.
- **A `.license` sidecar for every file that can't hold a comment.** That means one extra file per JSON file. Those files are few and grouped by folder, so `REUSE.toml` covers them with fewer moving parts.

## Consequences

- A new file needs a header before CI passes. `just annotate <files>` writes one.
- Headers add a few lines to the top of each file.
- A new kind of file that can't hold a comment needs an entry in `REUSE.toml`. The failing `reuse lint` points at it.

## Enforcement

- `reuse lint` runs in CI (the "REUSE compliance" job) and in `just check`. With no catch-all, any file without a header or an annotation fails it.
- The bindings test checks that `src/bindings.ts` matches the generator's output, header included.
- Nothing checks that a package's `REUSE.toml` annotation matches its manifest's `license`. Only `content/core` exists, and review checks the annotation when a package is added.
