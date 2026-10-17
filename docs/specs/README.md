<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Specs

A spec describes one feature or system: what it does, its rules, its data, its UI, and the scenarios that prove it works. The process is set out in [ADR 0009](../adr/0009-specs-and-traceability.md). Copy [`TEMPLATE.md`](TEMPLATE.md) to start a new spec.

## Status

- **Draft:** a design document under discussion. It may already list proposed scenarios for review, but isn't checked by traceability.
- **Accepted:** has numbered scenarios. Every scenario must have a test.
- **Implemented:** every scenario has a passing test, and the feature has shipped.

## Scenarios

Each scenario has a heading made of its id and a title, followed by its steps:

```markdown
### COND-004 — Rest restores stamina overnight

- **Given** a player with 40 stamina and Work Ethic 60
- **When** the player rests in every slot of a day and the day ends
- **Then** the player's stamina is 70
```

Each id is the spec's prefix plus a three-digit number. Ids are never reused. A removed scenario keeps its heading, marked `(Withdrawn)`.

A test that implements a scenario carries the marker and the GWT structure:

```rust
#[test]
fn rest_restores_stamina_overnight() {
    // spec: COND-004
    // Given
    let mut player = PlayerBuilder::new().stamina(40).work_ethic(60).build();
    // When
    let rested = end_day(&mut player, &[Activity::Rest; 3]);
    // Then
    assert_eq!(rested.condition().stamina(), Stamina::new(70));
}
```

## Index

| Spec | Prefix | Status |
|---|---|---|
| [Condition](condition.md) | `COND` | Draft |
| [Attributes and overall](attributes.md) | `ATTR` | Implemented |
| [Champions and mastery](champions-and-mastery.md) | `CHAMP`, `MAST` | Draft |
| [Competitions](competitions.md) | `COMP` | Draft |
| [Content packages](packages.md) | `PKG` | Implemented |
| [World generation](world-generation.md) | `GEN` | Implemented |
| [Saves and data locations](saves.md) | `SAVE` | Implemented |
| [New Game, Load Game and the main menu](new-game.md) | `NEWG` | Implemented |
| [Roster and player profile](roster.md) | `ROST` | Implemented |
