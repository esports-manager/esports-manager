<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# World generation

- **Prefix:** `GEN`
- **Status:** Implemented
- **Related:** [ADR 0002](../adr/0002-genre-seam.md), [ADR 0003](../adr/0003-deterministic-simulation.md), [packages](packages.md), [attributes](attributes.md), [core world](../game-design/core-world.md)

## Summary

At New Game, the loaded packages and a world seed are compiled into a world: regions, competitions, teams, and the players on every roster. Packages define the structure, and may pin some players; the generator fills in everyone else. It has to make strong teams strong and weak teams weak, give players a profile that fits their role, and produce the same world from the same seed on every machine.

The numbers are starting values, to be tuned in sim-bench.

## Rules

### Ownership

- **`domain`** (`domain::generation`, ADR 0002): the rules every genre shares. Normal draws, clamping and rounding of ratings, team strength, ages and birth dates, nationality and name choice, nicknames, the core traits drawn the same way everywhere (Aggression, Work Ethic, Consistency) and the potential formula, and the generic constants of `generation/`.
- **`esports::moba`:** roles, the seven MOBA skills, role bias, and the roster shape (five roles, seven players). Teamwork and Composure are core attributes, but in a MOBA they count toward overall, so they are drawn here with the skills and the role bias. The MOBA overall feeds the potential formula. The order of every draw is the genre's: it calls the `domain` rules in a fixed sequence.
- **`app`:** the use case that runs the generator over loaded content and hands the world to the save port.

### Randomness

- Every draw comes from a named stream derived from the world seed (ADR 0003):
  - `generator:team:<team id>` for a team's generated players and its sub roles
  - `generator:player:<player id>` for the generated fields of a pinned player
  - `generator:nickname:<player id>` for nicknames
- **Generated players' ids** are `player:<team slug>.<n>`, numbered from 1 in generation order within the team. Package slugs can't contain `.`, so a generated id never collides with a pinned one. The id is stable for the life of the save.
- Teams are generated in id order.
- Adding a team to a package doesn't change any other team's players. The one exception is a nickname that would collide with the new team's.
- **Normal draws are portable.** They use Box–Muller with the pure-Rust `libm` functions, not `f64::ln`/`cos`, which call the platform's maths library and can differ in the last bit between operating systems. Every rating is rounded to hundredths before it is stored.

### Team strength (`domain`, constants in `generation/`)

Reputation is 1–100 on each team, and each region has a `level` offset.

- **mu_team** = 35 + 0.4 × reputation + region level
- **sigma_team** = max(2, 12 − 0.07 × reputation)

A higher reputation gives a higher mean and a lower spread, as decided. With the core regions (Seorabeol +4, Pindorama −4):

| Team | Reputation | mu | sigma |
|---|---|---|---|
| Top Seorabeol team | 95 | 77 | 5.4 |
| Bottom Seorabeol team | 35 | 53 | 9.6 |
| Top Pindorama team | 85 | 65 | 6.1 |
| Bottom Pindorama team | 30 | 43 | 9.9 |

### Players: a two-level draw

1. **Player base:** b ~ N(mu_team, sigma_team).
2. **Each attribute that counts toward overall:** a ~ N(b + bias(role, attribute), 6), clamped to 1–99. That means the seven MOBA skills plus Teamwork and Composure.
3. **Role bias** comes from the overall weight table, the same table [attributes](attributes.md) uses. It is the single source of what a role values. bias = 8 × (w − w̄) / w̄, where w is the attribute's weight for that role and w̄ is the role's mean weight.
   - Example: Mechanics for a mid, weight 20 against a mean of 11.1, gets +6.4. Shotcalling for a mid, weight 6, gets −3.7.
4. **Aggression and Work Ethic:** N(50, 15). They are style and growth, not strength.
5. **Consistency** (hidden): N(55, 15).
6. **Potential** (hidden): max(overall, N(overall + 2.5 × max(0, 24 − age), 6)), clamped to 1–99. Young players have more room to grow.

All ratings are clamped to 1–99, never folded with `abs()`. Folding is what piled the Python generator's bad rolls up near the bottom.

### Roster shape (`esports::moba`)

- **The roster shape comes from the package's role set:** one player per role, plus `subs` more (2 in core), whose roles are different roles drawn from the team's stream. With core's five roles that is seven players. `subs` can't exceed the number of roles.
- **Pinned players count toward the roster.** Generation fills the remaining slots so the shape still holds. A team's pinned players must leave a completable roster: no more than the roster size, no role more than twice, and enough free slots for every role that has no pinned player. Otherwise it is a package error. For example, six pinned players split two-two-two across three roles leave one slot for two missing roles.
- **Starters:** for each role, the player with the highest overall starts. Ties go to the lower player id.
- Each player has one main role. A secondary role is left for later.

### Age and dates (`domain`)

- The world starts on `world.json`'s `start_date`. In core that is 2027-01-01, the first day of Season 1. The season number is game state, not package text.
- **Generated age:** N(22, 2.5), rounded, clamped to 17–28.
- **Birth date:** drawn uniformly among the dates that give exactly that age on the start date.
- Ages are always computed from the birth date and the current game date. They are never stored.

### Nationality and names (`domain`)

- A player's nationality is drawn from their region's weighted `nationalities` mix.
- **Given and family names** come from that nationality's pools. They are displayed in the nationality's `name_order`.
- **Nicknames** come from one shared pool and are unique in the world, ignoring case. Each player draws from the whole pool with their own stream and redraws while the nickname is taken; after 32 tries they draw among the unused entries, so generation always terminates. Another team's players can change a nickname only by taking the very one drawn. Pinned nicknames are taken out of the pool first.
- **Name and nickname pools are sorted before any draw**, so how a package splits them across files never changes the world (packages spec: file names carry no meaning).

### Pinned players (`esports::moba`)

A pinned player in `players/` keeps every field it sets, exactly. Every field it leaves out is generated as if the player were generated for that team, from the player's own stream. Pinned ratings are checked to be within 1–99 when the package loads. A pinned Potential is kept even if it ends up below the player's overall: that is a player at their ceiling.

### Checked when the package loads (`packages`)

A package that fails any of these is rejected before generation, so New Game never fails part-way:

- Every region's nationality mix has non-negative weights with a positive total.
- Every nationality a region can draw, or a pinned player names, has non-empty given-name and family-name pools. A pinned player draws names too, even with both pinned, so pinning never shifts another draw.
- The role set is non-empty with no duplicates, and `subs` doesn't exceed its size.
- Pinned nicknames are unique, ignoring case.
- The nickname pool has at least three times as many distinct entries (ignoring case), after pinned nicknames are removed, as there are generated players.
- Every team's pinned players leave a completable roster.

### Reproducibility

A seed reproduces a world **with the same packages and the same game version**. The save records each package's id, version and content hash next to the seed and the game version ([saves](saves.md)), so a bug report can rebuild the exact world.

## Scenarios

### GEN-001 — Same packages and seed, same world

- **Given** the core package and world seed 42
- **When** the world is generated twice, in separate processes
- **Then** both worlds are identical, field by field

### GEN-002 — A different seed changes the players, not the structure

- **Given** the core package
- **When** worlds are generated with seeds 1 and 2
- **Then** both have the same regions, competitions and teams, and their generated players differ

### GEN-003 — The same world on every operating system

- **Given** the core package and world seed 42
- **When** the world is generated on Linux, Windows and macOS
- **Then** each matches the same committed snapshot

### GEN-004 — Every roster has the right shape

- **Given** any world generated from the core package
- **When** each team's roster is inspected
- **Then** it has seven players, every role at least once, and its two extra players in two different roles

### GEN-005 — The best player in each role starts

- **Given** a team with two mids whose overalls are 71 and 68
- **When** its starters are chosen
- **Then** the 71 mid starts and the 68 mid is a sub

### GEN-006 — Ties for a starting place go to the lower id

- **Given** a team with two supports of equal overall, `player:a` and `player:b`
- **When** its starters are chosen
- **Then** `player:a` starts

### GEN-007 — Higher reputation means stronger players

- **Given** two teams in the same region with reputations 90 and 30
- **When** worlds are generated with 200 different seeds
- **Then** the reputation-90 team's mean player overall is higher, and the spread of its players' overalls is lower

### GEN-008 — The region level shifts every team

- **Given** two teams with reputation 60, one in a region with level +4 and one in a region with level −4
- **When** worlds are generated with 200 different seeds
- **Then** the team in the +4 region has the higher mean player overall

### GEN-009 — A role shapes the attributes

- **Given** worlds generated with 200 different seeds
- **When** generated mids are compared with generated supports
- **Then** the mids have the higher mean Mechanics, and the supports have the higher mean Shotcalling

### GEN-010 — Ratings stay in range at hundredths

- **Given** any generated world
- **When** every attribute of every player is inspected
- **Then** each one is between 1.00 and 99.00 and is stored in whole hundredths

### GEN-011 — Ages and birth dates agree

- **Given** any generated world with start date 2027-01-01
- **When** every player whose age and birth date aren't pinned is inspected
- **Then** each one's age on the start date is between 17 and 28, and is the age their birth date gives

### GEN-012 — Nationalities follow the region's mix

- **Given** a region whose mix is 94% `nationality:kr`
- **When** worlds are generated with 200 different seeds
- **Then** between 90% and 98% of the region's generated players are Korean

### GEN-013 — Names come from the nationality's pools

- **Given** any generated world
- **When** each generated player is inspected
- **Then** their given and family names are both in their nationality's pools

### GEN-014 — Nicknames are unique

- **Given** any generated world
- **When** every player's nickname is compared
- **Then** no two players share one, ignoring case

### GEN-015 — A pinned player keeps every pinned field

- **Given** a pinned player with nickname, role, birth date and Mechanics 95, and no other fields
- **When** the world is generated
- **Then** those four values are exactly as pinned, and every other field is generated and in range

### GEN-016 — Adding a team leaves the others alone

- **Given** worlds generated with seed 42 from the core package, and from the core package plus one more team
- **When** the existing teams' players are compared
- **Then** their attributes, ages, nationalities, and given and family names are identical

### GEN-017 — Potential is never below current ability

- **Given** any generated world
- **When** every generated player is inspected
- **Then** each one whose Potential isn't pinned has a Potential of at least their overall

### GEN-018 — Generated players get stable, distinct ids

- **Given** a world generated with seed 42
- **When** the save is closed and opened again
- **Then** every generated player has the same `player:<team slug>.<n>` id as before, and none equals a pinned player's id

### GEN-019 — The roster shape follows the role set

- **Given** a test package with three roles and `subs` 1
- **When** its world is generated
- **Then** every team has four players, one per role and one sub

### GEN-020 — A roster pinned into a corner is a package error

- **Given** a team with six pinned players, two each in Top, Mid and Bot
- **When** the package is loaded
- **Then** the report has an incompletable-roster error for that team, naming Jungle and Support

### GEN-021 — Invalid nationality mixes are package errors

- **Given** a region whose mix is empty, and another whose weights are all zero
- **When** the package is loaded
- **Then** the report has an invalid-mix error for each region

### GEN-022 — Every drawable nationality needs names

- **Given** a region that can draw `nationality:se`, with no Swedish family names
- **When** the package is loaded
- **Then** the report has an empty-pool error for `nationality:se` and family names

### GEN-023 — Too few distinct nicknames is a package error

- **Given** a nickname pool of 400 entries, of which only 300 differ when case is ignored, for 126 generated players
- **When** the package is loaded
- **Then** the report has a nickname-pool error giving 300 distinct and 378 needed

### GEN-024 — Duplicate pinned nicknames are a package error

- **Given** two pinned players with the nicknames "Kairos" and "kairos"
- **When** the package is loaded
- **Then** the report has a duplicate-nickname error naming both players

## Enforcement

- **The RNG lint (ADR 0003)** covers only `domain`, `esports` and `app` today, so it is extended to `packages` and `db`, which now have code.
- GEN-003 runs on every OS in CI. It fails if any platform's floats differ.

## Open questions

- Secondary roles, and players who can flex into them.
- Tuning the constants, in sim-bench, once the match simulation exists.
- A generated staff member (the assistant coach) is an MVP feature, not part of the skeleton.
