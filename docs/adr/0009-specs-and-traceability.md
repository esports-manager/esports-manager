<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# 0009. Specs with Given/When/Then scenarios, traced to tests

- **Status:** Accepted
- **Date:** 2026-10-15
- **Related:** [0008](0008-enforcement-policy.md), [specs/README.md](../specs/README.md)

## Context

We plan before we code: every feature is specified before it's implemented, and every behaviour in the spec has a test. Specs written apart from tests drift; tests written without a spec lose the intent.

## Decision

- **A feature spec** is a Markdown file in `docs/specs/`. It holds the design, the rules, the data involved, wireframes for any UI (wide and compact layouts), and **numbered scenarios**.
- **A scenario** has an id made of the spec's prefix and a three-digit number (`DRAFT-007`), a title, and `Given` / `When` / `Then` steps. Ids are never reused or renumbered; a removed scenario keeps its id with status *Withdrawn*.
- **Every scenario is implemented by at least one test**, which carries a `spec: DRAFT-007` marker in a comment and follows the `// Given` / `// When` / `// Then` structure. Tests can be Rust unit or integration tests, Vitest tests, or Playwright tests.
- **Tests come first.** For each scenario, the test is written and seen to fail before the implementation makes it pass. Agents and humans both follow this.
- **The workflow for a feature:**
  1. spec (plus an ADR if a structural decision is involved)
  2. tests tagged with scenario ids
  3. implementation
  4. `just check` green
  5. review
  6. PR
- A *Draft* spec is a design document. It may list proposed scenarios so they can be reviewed before any code, but it isn't traced. It becomes *Accepted*, and traceable, in the PR that implements its scenarios.

## Alternatives considered

- **Gherkin `.feature` files run with `cucumber-rs`.** Executable, but it adds a step-definition glue layer, which tends to bloat and which refactoring tools can't follow.
- **GWT as a naming convention only.** No traceability, so specs and tests drift apart.

## Consequences

- Specs stay readable as design documents.
- A reviewer can check coverage of intent by reading the scenario list.

## Enforcement

A traceability script runs in `just check` and fails if:

- a scenario id in an *Accepted* spec has no test referencing it
- a test references a scenario id that doesn't exist or is *Withdrawn*
- two scenarios share an id
