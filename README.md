<!--
SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
SPDX-License-Identifier: GPL-3.0-or-later
License-Filename: LICENSES/GPL-3.0-or-later
-->

<div align="center">

![eSports Manager Logo](docs/img/logo.svg)

# eSports Manager

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Last commit](https://img.shields.io/github/last-commit/esports-manager/esports-manager)](https://github.com/esports-manager/esports-manager/commits/develop)
[![GitHub contributors](https://img.shields.io/github/contributors/esports-manager/esports-manager.svg)](https://GitHub.com/esports-manager/esports-manager/graphs/contributors/)

**A free and open source esports management game**

⚠️ **Development status:** the game is being rewritten from scratch in Rust, Tauri and React/TypeScript. Nothing is playable yet. The previous Python implementation is preserved at the [`python-final`](https://github.com/esports-manager/esports-manager/tree/python-final) tag. ⚠️

</div>

---

**eSports Manager** is a single-player management game in the tradition of Football Manager and Bygfoot, set in the world of competitive gaming. You take charge of a professional esports team and guide it to glory:

- Build your roster, and find new talent in solo queue
- Plan the week: scrims with other teams, solo queue, rest. Watch your players' stamina
- Develop your players and teach them new champions
- Study and call the draft, set the game plan, and adjust it live
- Talk to your players between games of a series
- Compete in leagues and tournaments to meet your board's objectives

The first genre is a **MOBA**, with other MOBAs, RTS and FPS games planned to follow. The world is entirely **fictional**, and **modding is first-class**: the base game is itself a content package, and you can build your own worlds with your own regions, leagues, teams, players and champions.

The game will be available in English and Brazilian Portuguese, on Linux, Windows and macOS, with Android planned.

## Documentation

- [Game design overview](docs/game-design/overview.md) and [MVP scope](docs/game-design/mvp.md)
- [Roadmap](docs/roadmap.md)
- [Architecture Decision Records](docs/adr/README.md)
- [Specs](docs/specs/README.md)

## Building from source

There is nothing to play yet. To build the workspace and run the tests, install [rustup](https://rustup.rs/), [`just`](https://just.systems/), Node.js with pnpm, and the [Tauri prerequisites](https://tauri.app/start/prerequisites/) for your OS, then:

```bash
git clone https://github.com/esports-manager/esports-manager.git
cd esports-manager
rustup toolchain install   # installs the pinned toolchain
just install               # frontend dependencies
just test
just dev                   # opens the (still empty) desktop app
```

[CONTRIBUTING.md](CONTRIBUTING.md#development-setup) covers the full development setup and `just check`.

## Contributing

Contributions are welcome: code, design, writing, translation, testing and ideas. Start with [CONTRIBUTING.md](CONTRIBUTING.md), which covers the architecture, the workflow (spec → tests → implementation) and the quality gates every change must pass.

## Contact

- **Email:** admin@esportsmanager.net
- **[Discussions](https://github.com/esports-manager/esports-manager/discussions)**
- **[GitHub Issues](https://github.com/esports-manager/esports-manager/issues)**, for bug reports and feature requests

## License

eSports Manager is licensed under the GNU General Public License, version 3 or later. This covers both the code and the base-game content.

```
eSports Manager - A free and open source eSports management game
Copyright (C) 2020-2026  Pedrenrique G. Guimarães

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
```

For the full license text, see [LICENSE.md](LICENSE.md).
