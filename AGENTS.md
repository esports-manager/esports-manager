<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Agent instructions

This file is an index. The rules themselves live in human-facing documents. Read them, and don't treat anything here as a substitute.

- **How we work, architecture rules, quality gates:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Why things are the way they are:** [docs/adr/](docs/adr/README.md)
- **What the game is:** [docs/game-design/overview.md](docs/game-design/overview.md), [docs/game-design/mvp.md](docs/game-design/mvp.md)
- **What a feature must do:** [docs/specs/](docs/specs/README.md)

Before you start:

1. Find the spec for the feature. If none exists, write it first; don't code from a chat description.
2. Search for an existing implementation of any concept before adding one. Duplicated logic is a bug (CONTRIBUTING rule 1).
3. Write the tests first, tagged with scenario ids.
4. Run `just check` before you call the work done, and report its real output.
