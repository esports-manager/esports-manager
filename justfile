# SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Every quality gate, runnable locally exactly as CI runs it (ADR 0008).
# `just` lists the recipes; `just check` runs them all.

set shell := ["bash", "-euo", "pipefail", "-c"]

# Branch that `mutants` compares against.
base := "origin/develop"

default:
    @just --list

# Run every gate. CI runs this same recipe.
check: rust-check frontend-check e2e smoke reuse mutants

# Rust gates.
rust-check: fmt-check clippy arch vocab trace rest-patterns coverage deny machete

# Frontend gates.
frontend-check: typecheck lint knip coverage-frontend

# Install frontend dependencies exactly as locked.
install:
    pnpm install --frozen-lockfile

# Install the fast pre-commit hooks (lefthook.yml).
hooks:
    pnpm hooks

# Run the desktop app with hot reload.
dev:
    pnpm tauri dev

# Regenerate src/bindings.ts from the Tauri commands (ADR 0006).
bindings:
    UPDATE_BINDINGS=1 cargo test --locked -p esports-manager typescript_bindings_are_up_to_date

# Regenerates crates/db/src/schema.rs from the migrations (ADR 0004). Needs
# diesel_cli: `cargo install diesel_cli --no-default-features --features sqlite-bundled`.
db-schema:
    mkdir -p target
    rm -f target/schema.db
    cd crates/db && diesel migration run --database-url ../../target/schema.db
    rustfmt --edition 2024 crates/db/src/schema.rs

# Regenerates the backend views the browser E2E tests answer with.
e2e-fixtures:
    UPDATE_FIXTURES=1 cargo test --locked -p cli --test e2e_fixtures

# Regenerates the package JSON Schemas in content/schemas from the Rust types (ADR 0005).
schemas:
    UPDATE_SCHEMAS=1 cargo test --locked -p packages json_schemas_are_up_to_date

# Format all Rust and frontend code.
fmt:
    cargo fmt --all
    pnpm format

fmt-check:
    cargo fmt --all --check

clippy:
    cargo clippy --workspace --all-targets --locked -- -D warnings

# Fast test run without coverage instrumentation.
test:
    cargo test --workspace --locked

# Crate graph matches ADR 0001.
arch:
    cargo xtask arch

# No genre vocabulary in the core crate (ADR 0002).
vocab:
    cargo xtask vocab

# Every scenario in an accepted spec has a test (ADR 0009).
trace:
    cargo xtask trace

# No rest patterns in package conversion modules (ADR 0005).
rest-patterns:
    cargo xtask rest-patterns

# Runs the tests with coverage and checks each crate's minimum (quality.toml).
coverage:
    cargo llvm-cov --workspace --exclude xtask --locked --json --summary-only --output-path target/llvm-cov.json
    cargo xtask coverage target/llvm-cov.json

# HTML coverage report in target/llvm-cov/html.
coverage-html:
    cargo llvm-cov --workspace --exclude xtask --locked --html

typecheck:
    pnpm typecheck

# Biome lint and format check.
lint:
    pnpm lint

# No unused files, exports or dependencies.
knip:
    pnpm knip

# Vitest with coverage minimums (vite.config.ts).
coverage-frontend:
    pnpm coverage

# First run: `pnpm exec playwright install chromium`.
# Browser E2E tests at desktop and compact sizes, with axe.
e2e:
    pnpm e2e

# Needs tauri-driver, and WebKitWebDriver plus xvfb-run on Linux. GTK is
# kept off any Wayland session, which WebKitWebDriver sessions crash on.
# Start the real desktop binary and check the UI reaches the backend.
smoke:
    pnpm tauri build --debug --no-bundle
    cargo build -p cli
    {{ if os() == "linux" { "env -u WAYLAND_DISPLAY GDK_BACKEND=x11 xvfb-run -a pnpm smoke" } else { "pnpm smoke" } }}

# Licences, bans and sources. Advisories run weekly in CI (`just advisories`).
deny:
    cargo deny --locked check bans licenses sources

advisories:
    cargo deny --locked check advisories

machete:
    cargo machete

reuse:
    reuse lint

# `reuse` reads `.ftl` as FreeMarker, so Fluent files get `#` comments by hand.
# Writes the licence header into new files (ADR 0012): `just annotate a.rs b.ts`.
annotate +files:
    #!/usr/bin/env bash
    set -euo pipefail
    args=(--copyright="Pedrenrique G. Guimarães <admin@esportsmanager.net>" --year="$(date +%Y)" --license=GPL-3.0-or-later --skip-existing)
    for file in {{files}}; do
        case "$file" in
            *.ftl | justfile) reuse annotate "${args[@]}" --style=python "$file" ;;
            *) reuse annotate "${args[@]}" "$file" ;;
        esac
    done

# Mutation testing on the code changed since `base` (ADR 0008).
mutants:
    mkdir -p target
    git diff "$(git merge-base {{base}} HEAD)" > target/mutants.diff
    cargo mutants --workspace --in-diff target/mutants.diff

# Full mutation run (weekly in CI).
mutants-all:
    cargo mutants --workspace
