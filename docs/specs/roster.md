<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# Roster and player profile

- **Prefix:** `ROST`
- **Status:** Implemented
- **Related:** [attributes](attributes.md), [world generation](world-generation.md), [new game](new-game.md), [ADR 0006](../adr/0006-bindings-and-pure-view.md), [ADR 0010](../adr/0010-fictional-world-and-licensing.md)

## Summary

The roster is the first screen of a game: who is on the team, in which roles, and how good they are. The profile is one player in detail, with their attributes. These are the walking skeleton's proof that the whole pipeline works, from the package through the generator and the save to the screen.


## Rules

### Queries (`app`)

- **`roster_view(save, team)`** returns, already derived:
  - **team:** name message id, tag, colours, region, and its league (competition id and name message id) for the header
  - **players:** for each one, id, nickname, given and family name, name order, role, starter or sub, nationality (id and code), age and overall
- **`player_profile(save, player)`** returns:
  - the same identity fields, plus team and birth date
  - **skills** and **traits**, as whole-number values
  - **hidden attributes**, as unknown, with no value ([attributes](attributes.md))
- The team defaults to the user's team.

### Order

- **Starters first, then subs.** Each group is in role-set order (Top, Jungle, Mid, Bot, Support), and players with the same role are ordered by nickname.
- The UI may re-sort the table by a column. That only reorders the values it received; it doesn't derive anything.

### Display

- **Age:** completed years on the current game date, computed in Rust.
- **Full name:** in the nationality's order. The UI renders it with one Fluent message that selects on name order. Korean, Chinese and Vietnamese players are family-first; everyone else is given-first.
- **Nationality:** a badge with the uppercase country code (`KR`). Its accessible name is the country's name. The profile shows the name in full. Flag art comes later as package assets.
- **Crest:** a monogram of the team tag on the team's first colour, bordered in its second (ADR 0010). The view also carries the monogram's text colour, which Rust picks (black or white) so the contrast against the first colour meets WCAG AA.
- **Overall:** a whole number ([attributes](attributes.md)).
- **Attribute names and their groups** are UI messages, because attributes are defined in code. **Role, team, region and country names** are package messages, because the package defines them.

## UI

### Roster

```
Wide (≥ 1024 px)
┌───────────────────────────────────────────────────────────────────┐
│ (AZT) Azure Tigers · Seorabeol Pro League                         │
│                                                                   │
│ Starters                                                          │
│ Role     Nickname   Name               Nat.  Age   Overall        │
│ Top      Granite    Kim Seo-jun        KR    23    74             │
│ Jungle   Hollow     Lee Ha-eun         KR    21    77             │
│ Mid      Kairos     Han Do-yun         KR    29    93             │
│ Bot      …                                                        │
│ Support  …                                                        │
│ Subs                                                              │
│ Mid      …                                                        │
│ Support  …                                                        │
└───────────────────────────────────────────────────────────────────┘

Compact (< 640 px): the table becomes a list of cards
┌──────────────────────────┐
│ (AZT) Azure Tigers       │
│ Starters                 │
│ ┌──────────────────────┐ │
│ │ Mid · Kairos     93  │ │
│ │ Han Do-yun · KR · 29 │ │
│ └──────────────────────┘ │
│  …                       │
│ Subs                     │
│  …                       │
└──────────────────────────┘
```

- Every row and card is a link to the player's profile. It is reachable with Tab, opens with Enter, and is at least 44 px tall.
- Column headers are buttons that sort; `aria-sort` reflects the current order.

### Player profile

```
Wide                                               Compact
┌─────────────────────────────────────────────┐    ┌──────────────────────┐
│ ← Roster                                    │    │ ← Roster             │
│ Kairos                          Overall 93  │    │ Kairos           93  │
│ Han Do-yun · Mid · 29 · South Korea (KR)    │    │ Han Do-yun · Mid     │
│ Azure Tigers · born 14 Mar 1997             │    │ 29 · South Korea     │
│                                             │    │──────────────────────│
│ Skills                Traits                │    │ Skills               │
│ Mechanics       95    Teamwork      82      │    │ Mechanics        95  │
│ Laning          88    Aggression    61      │    │ …                    │
│ Game Sense      97    Composure     96      │    │ Traits               │
│ Awareness       90    Work Ethic    84      │    │ …                    │
│ Positioning     91                          │    │ Hidden               │
│ Pool Breadth    87    Hidden                │    │ Consistency       ?  │
│ Shotcalling     85    Consistency    ?      │    │ Potential         ?  │
│                       Potential      ?      │    │                      │
└─────────────────────────────────────────────┘    └──────────────────────┘
```

- **Unknown** shows as `?` with the accessible name "unknown" in the current locale.
- Back returns to the roster with its sort order kept.

## CLI

```
esm roster --save <name> [--team <team-id>]
esm player --save <name> <player-id>
```

The `--json` output is the same DTO the UI receives.

## Scenarios

### ROST-001 — Starters, then subs, in role order

- **Given** a new game
- **When** the roster view of the user's team is built
- **Then** it lists five starters, one per role in the order Top, Jungle, Mid, Bot, Support, followed by the two subs in role order

### ROST-002 — Each row carries what the table shows

- **Given** a new game
- **When** the roster view is built
- **Then** every player has a role, a nickname, a given and family name with a name order, a nationality code, an age and an overall

### ROST-003 — Names follow the nationality's order

- **Given** a Korean player Han Do-yun and a Brazilian player Caio Ribeiro
- **When** their full names are shown
- **Then** they read "Han Do-yun" and "Caio Ribeiro"

### ROST-004 — Age counts completed years on the game date

- **Given** the game date 2027-01-01 and a player born on 2000-01-02
- **When** the roster view is built
- **Then** their age is 26

### ROST-005 — The overall shown is the attributes spec's overall

- **Given** a player whose stored overall is 74.50
- **When** the roster view is built
- **Then** their overall is 75

### ROST-006 — The profile shows skills and traits, and hides hidden attributes

- **Given** a player in a new game
- **When** their profile is built
- **Then** it has seven skills and four traits with whole-number values, and Consistency and Potential are unknown

### ROST-007 — The roster opens a profile from the keyboard

- **Given** the roster screen
- **When** the user tabs to a player and presses Enter
- **Then** that player's profile is shown, and Back returns to the roster

### ROST-008 — The compact roster is a card list

- **Given** the roster screen at phone width
- **When** it is shown
- **Then** players are cards with role, nickname, name, nationality, age and overall, and the page doesn't scroll horizontally

### ROST-009 — The roster and profile are translated

- **Given** the locale `pt-BR`
- **When** the roster and a profile are shown
- **Then** role names, attribute names, group headings and the country name are in Portuguese

### ROST-010 — The crest's text is readable

- **Given** any team in the core package
- **When** its crest is built
- **Then** the monogram's text colour has a contrast of at least 4.5:1 against the team's first colour

### ROST-011 — The CLI and the UI see the same roster

- **Given** a new game
- **When** `esm roster --json` runs, and the desktop app requests the roster view
- **Then** both return the same view

### ROST-012 — Both screens pass the accessibility audit

- **Given** the roster and a profile
- **When** each is shown in the wide and the compact layout
- **Then** axe reports no violations
