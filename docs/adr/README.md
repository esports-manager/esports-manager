<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Architecture Decision Records

An ADR records one decision that shapes the codebase: the context, the choice, what it costs, and how the choice is enforced. We use a trimmed [MADR](https://adr.github.io/madr/) format; copy [`template.md`](template.md) to start a new one.

## Rules

- One decision per ADR. Number them sequentially and never reuse a number.
- An ADR is **Proposed** while under discussion, **Accepted** once merged, and **Superseded by NNNN** when replaced. Accepted ADRs are not edited except to change their status or fix typos; a changed decision gets a new ADR.
- Every ADR has an **Enforcement** section. A decision that no compiler, lint, test or CI check enforces must say so explicitly and say why (see [ADR 0008](0008-enforcement-policy.md)).
- Write an ADR when a change adds or moves a crate boundary, adds a dependency that other code will build on, changes the save or package format, or changes a rule in `CONTRIBUTING.md`.

## Index

| #    | Title                                                                        | Status   |
|------|------------------------------------------------------------------------------|----------|
| 0001 | [Clean Architecture and workspace layout](0001-clean-architecture-and-workspace-layout.md) | Accepted |
| 0002 | [Genre seam: genre-agnostic core, one genre per save](0002-genre-seam.md)      | Accepted |
| 0003 | [Deterministic simulation](0003-deterministic-simulation.md)                 | Accepted |
| 0004 | [SQLite as the source of truth, accessed through Diesel](0004-sqlite-and-diesel.md) | Accepted |
| 0005 | [`.esm` content packages](0005-esm-packages.md)                              | Accepted |
| 0006 | [Generated bindings; the frontend is a pure view](0006-bindings-and-pure-view.md) | Accepted |
| 0007 | [Internationalization with Project Fluent](0007-i18n-fluent.md)              | Accepted |
| 0008 | [Enforcement policy and quality gates](0008-enforcement-policy.md)          | Accepted |
| 0009 | [Specs with Given/When/Then scenarios, traced to tests](0009-specs-and-traceability.md) | Accepted |
| 0010 | [Fictional world, licensing and assets](0010-fictional-world-and-licensing.md) | Accepted, amended by 0011 and 0012 |
| 0011 | [A package's licence is declared in its manifest](0011-package-licence-in-the-manifest.md) | Accepted |
| 0012 | [Every file that can hold a comment carries its licence header](0012-licence-headers-in-every-file.md) | Accepted |
