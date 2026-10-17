<!--
SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
SPDX-License-Identifier: GPL-3.0-or-later
License-Filename: LICENSES/GPL-3.0-or-later
-->

# Contributing to eSports Manager

Thank you for your interest in eSports Manager. This document is the **single source of truth** for how we work. Agent instruction files (`CLAUDE.md`, `AGENTS.md`) only point here; if a rule isn't written in this file or in `docs/`, it isn't a rule.

## Ways to help

- **Report a bug** or **propose a feature** using the issue templates. Search existing issues first.
- **Design:** UI mockups, the visual identity, game systems.
- **Writing and content:** champions, teams, regions and narration for the fictional world. All content must be original (see [ADR 0010](docs/adr/0010-fictional-world-and-licensing.md)).
- **Translation:** the game uses [Project Fluent](https://projectfluent.org/) `.ftl` files. English and Brazilian Portuguese ship first.
- **Code:** read the rest of this document.

We follow our [Code of Conduct](CODE_OF_CONDUCT.md). Report unacceptable behaviour to admin@esportsmanager.net.

## Licensing

All code and base-game content are **GPL-3.0-or-later**. By contributing, you confirm that your contribution is your own original work, or is compatible with that licence, and contains no third-party trademarks or copyrighted material. The repository is [REUSE](https://reuse.software/)-compliant ([ADR 0012](docs/adr/0012-licence-headers-in-every-file.md)): every file that can hold a comment starts with an SPDX licence header, and `REUSE.toml` covers only files that can't, such as JSON and images. `just annotate <files>` writes the header for a new file. Any third-party file must declare its own author and licence.

## Architecture in one page

The structural decisions are in [`docs/adr/`](docs/adr/README.md). The essentials:

```
crates/domain     genre-agnostic core; pure Rust, no IO, no wall-clock
crates/esports    genre modules (esports::moba)              → domain
crates/app        use cases, ports, view DTOs                → domain, esports
crates/packages   .esm package loading and validation        → domain, esports, app
crates/db         SQLite via Diesel                           → domain, esports, app
crates/cli        headless adapter + sim-bench                → app, packages, db
src-tauri/        desktop adapter (thin)                      → app, packages, db
src/              React/TypeScript UI (a pure view)
content/core/     the base game, as an .esm package
```

Rules that most often matter in review:

1. **Every concept has exactly one home.** Before you write a helper, search for an existing one. If two crates need it, move it down; never copy it. Duplicated logic is a bug.
2. **Game rules live in Rust.** Adapters translate and call one use case. The frontend renders view DTOs and localizes; it never computes game values ([ADR 0006](docs/adr/0006-bindings-and-pure-view.md)).
3. **Everything is deterministic.** Domain code receives an RNG and never creates one; there is no wall-clock in the domain, and no `HashMap` where iteration order matters ([ADR 0003](docs/adr/0003-deterministic-simulation.md)).
4. **No prose from the backend.** Emit a Fluent message id plus typed arguments, and do the same for errors ([ADR 0007](docs/adr/0007-i18n-fluent.md)).
5. **The domain doesn't know about storage.** Diesel stays in `db`, and the domain never sees a row struct ([ADR 0004](docs/adr/0004-sqlite-and-diesel.md)).
6. **No MOBA words in `domain`** ([ADR 0002](docs/adr/0002-genre-seam.md)).

## Workflow

Every feature follows the same path ([ADR 0009](docs/adr/0009-specs-and-traceability.md)):

1. **Spec.** Write or extend a spec in [`docs/specs/`](docs/specs/README.md) with numbered Given/When/Then scenarios, plus wide and compact wireframes if it has UI. If the feature changes structure, write an ADR too.
2. **Tests first.** Write tests for each scenario, tagged `spec: XXXX-NNN`, structured as `// Given` / `// When` / `// Then`. Watch them fail.
3. **Implement** until the tests pass. Then refactor.
4. **`just check`** must be green locally.
5. **Open a PR** against `develop`. The PR title follows Conventional Commits. Link the spec and the issue.

Tests must be meaningful: mutation testing runs on every PR, and a surviving mutant means a test doesn't actually check the behaviour.

## Quality gates

Every gate is enforced; there are no advisory checks ([ADR 0008](docs/adr/0008-enforcement-policy.md)). If a gate is wrong, change it in a PR, don't work around it.

- **Rust:** `cargo fmt`, `clippy` (pedantic, no `unwrap`/`expect`/`panic` outside tests, no wildcard enum arms, no `unsafe`), the architecture test, coverage thresholds per crate, `cargo-mutants` on the diff, `cargo-deny`, `cargo-machete`.
- **Frontend:** TypeScript strict, Biome, knip, Vitest with coverage minimums, Playwright at desktop and compact sizes with axe accessibility checks, and a smoke test of the real desktop binary through `tauri-driver`.
- **Cross-cutting:** generated bindings and JSON Schemas up to date, locale coverage, spec-to-test traceability, `reuse lint`, Conventional Commits.

`just check` runs all of them, and CI runs the same recipes. The thresholds, the allowed crate graph and the denied genre words live in [`quality.toml`](quality.toml). Lowering a threshold or allowing a new dependency edge is a change to the ADR it comes from.

## Development setup

You need:

- [rustup](https://rustup.rs/). The toolchain version is pinned in `rust-toolchain.toml`; run `rustup toolchain install` in the repository to get it.
- [Node.js](https://nodejs.org/) (the version in `.node-version`) and [pnpm](https://pnpm.io/) (the version in `package.json` → `packageManager`).
- The [Tauri system prerequisites](https://tauri.app/start/prerequisites/) for your OS. On Debian/Ubuntu: `libwebkit2gtk-4.1-dev libxdo-dev libssl-dev libayatana-appindicator3-dev librsvg2-dev`; on Fedora: `webkit2gtk4.1-devel openssl-devel libxdo-devel libappindicator-gtk3-devel librsvg2-devel`.
- [`just`](https://just.systems/) to run the recipes.
- The gate tools: `cargo install --locked cargo-llvm-cov cargo-mutants cargo-deny cargo-machete`. `cargo binstall` is faster if you have it.
- [`reuse`](https://reuse.software/) (`pipx install reuse`) for the licence check.
- For the end-to-end gates: `pnpm exec playwright install chromium` (browser tests), and `cargo install --locked tauri-driver` plus WebKitWebDriver (`webkit2gtk-driver` on Debian/Ubuntu, part of `webkit2gtk4.1` on Fedora) and `xvfb-run` for the desktop smoke test.

Then:

```bash
just install    # frontend dependencies, as locked
just dev        # run the desktop app with hot reload
just            # list the recipes
just test       # fast Rust test run
just check      # every gate, as CI runs them
just fmt        # format Rust and frontend code
just bindings   # regenerate src/bindings.ts after changing a Tauri command or DTO
just schemas    # regenerate content/schemas after changing a package definition type
just db-schema  # regenerate crates/db/src/schema.rs after adding a migration (needs diesel_cli)
just e2e        # browser E2E tests (desktop and compact sizes, axe)
just smoke      # start the real desktop binary and check it talks to the backend
cargo run -p cli --bin esm   # the headless CLI
```

The repository checks that no off-the-shelf tool covers (crate graph, genre vocabulary, spec traceability, per-crate coverage, rest patterns in package conversion) live in [`xtask/`](xtask/src/main.rs) and run through `cargo xtask <check>`.

### Frontend layout

- `src/bindings.ts` is **generated** from the Rust commands and DTOs (ADR 0006). Never edit it; run `just bindings`. A test fails if it is out of date.
- `content/schemas/` and `crates/db/src/schema.rs` are generated too (`just schemas`, `just db-schema`), each with a drift test.
- A new migration needs a fixture save in `crates/db/tests/fixtures/`, written once with `UPDATE_FIXTURES=1`, and a test that opens it (ADR 0004).
- Call the backend only through `commands` from `src/bindings.ts`. Biome rejects direct `@tauri-apps/api/core` imports.
- **Data** goes through TanStack Query hooks in `src/hooks/` (one per backend query). There is no global store of game state.
- **Screens** are routes in `src/routes/`, registered in `src/router.tsx`.
- **Text:** every user-visible string is a Fluent message in `src/locales/<locale>/*.ftl`, with **every locale updated in the same change** (English and Brazilian Portuguese today). Use `<Localized id="…">` or `l10n.getString("…")` with a literal id. The i18n tests fail on a missing translation, a mismatched `$variable`, an unused message, or text written directly in JSX.
- **Styling:** Tailwind utilities backed by the tokens in `src/styles/tokens.css`. Don't hard-code colours. Every `--text-*` token must keep WCAG AA contrast on every `--surface-*` token; a test enforces it.
- **Logic** that isn't a component (formatting, i18n, checks) lives in `src/lib/` or `tools/`, where Vitest's 80% coverage minimum applies.
- **E2E tests** live in `e2e/` and run against `vite --mode e2e`, where `src/test/e2e-ipc.ts` answers backend commands. Add a handler there for each new command a screen calls.
- `just hooks` installs fast pre-commit checks (lefthook). They are optional; CI runs everything anyway.

## Commit messages

We follow [Conventional Commits](https://www.conventionalcommits.org/): `type(scope): subject`.

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`.

```
feat(moba): add mastery tier hysteresis
fix(db): order roster query by player id
docs(adr): record package override rules
```

## Branches

- `develop` is the integration branch, and every PR targets it.
- Name branches `type/short-description`, for example `feat/scrim-scheduling` or `fix/draft-ban-order`.
- Keep your branch rebased on `develop`. Every PR needs at least one maintainer approval and a green CI.

## Contact

- **Issues** for bugs and feature requests.
- **[Discussions](https://github.com/esports-manager/esports-manager/discussions)** for questions and ideas.
- **admin@esportsmanager.net** for private matters. Report security issues there, not in public.
