<!--
SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>

SPDX-License-Identifier: GPL-3.0-or-later
-->

# The core world

This is the content `content/core` ships for the walking skeleton. Every name here is original (ADR 0010). The two regions are *inspired by* the Korean and Brazilian scenes, but borrow nothing from their leagues, teams or players. Review should still check each name against real organizations before it is committed.

Accepted in review of PR #9.

## World

- **Start date:** 2027-01-01, labelled **Season 1**.
- **Countries:** Brazil, South Korea, China, the United States, Argentina, Sweden, Vietnam, Germany, France, Spain and Italy.
- **Names and countries:**
  - **Name order:** Korea, China and Vietnam are family-first; the others are given-first.
  - **How names are written:** Korean names use Revised Romanization and Chinese names Pinyin without tone marks. Vietnamese, Portuguese, Spanish, German, French, Swedish and Italian names keep their diacritics.
  - **Country names** are package text, in `en` and `pt-BR`.
- **Pool sizes:** at least 40 given names and 30 family names per country, and one shared pool of at least 400 nicknames that differ when case is ignored. 18 teams × 7 players is 126 players, and the pool must be at least three times the number of generated players.

## Regions

| | Seorabeol | Pindorama |
|---|---|---|
| Inspired by | Korea | Brazil |
| League | Seorabeol Pro League (SPL) | Liga Pindorama (LPD) |
| Teams | 10 | 8 |
| Level | +4 | −4 |
| Nationality mix | KR 94, CN 3, VN 3 | BR 79, AR 8, KR 4, US 2, ES 2, IT 2, FR 1, DE 1, SE 1 |

Seorabeol is the old name of the Silla capital, from which "Seoul" comes. Pindorama is the Tupi name for the land that became Brazil. In `pt-BR`, the SPL is "Liga Profissional Seorabeol"; the LPD keeps its name.

## Teams

### Seorabeol

| Team | Tag | Colours | Reputation |
|---|---|---|---|
| Azure Tigers | AZT | `#1E5AA8` `#F2C14E` | 95 |
| Crimson Dynasty | CDY | `#B3122E` `#1C1C1C` | 90 |
| Moonrise Gaming | MRG | `#3B2F6B` `#E8E4F2` | 82 |
| Iron Cranes | ICR | `#5A6470` `#E03A3E` | 75 |
| Haneul Esports | HNL | `#4FA3D9` `#FFFFFF` | 68 |
| Pulse Seven | PLS | `#E4572E` `#29335C` | 61 |
| Black Pine | BPN | `#1F3B2D` `#D9C38A` | 54 |
| Starfall | SFL | `#0B1D3A` `#F5D547` | 47 |
| Granite Wolves | GRW | `#6E6E6E` `#2F80ED` | 41 |
| Echo Phoenix | EPX | `#F28C28` `#5B2A86` | 35 |

### Pindorama

| Team | Tag | Colours | Reputation |
|---|---|---|---|
| Onça Gaming | ONC | `#D9A21B` `#1A1A1A` | 85 |
| Tempestade | TMP | `#2D3E8C` `#9AD0EC` | 77 |
| Arara Esports | ARA | `#E63946` `#1D7874` | 69 |
| Ipê Roxo | IPR | `#7B2D8E` `#F4E04D` | 61 |
| Maré Alta | MAR | `#0077B6` `#FFFFFF` | 53 |
| Capivara Club | CAP | `#8C5A3C` `#F2E8CF` | 46 |
| Raio Verde | RVD | `#1B9E4B` `#F7F7F7` | 38 |
| Sertão Kings | STK | `#C1440E` `#F6BD60` | 30 |

## Special players

You decided on a few hand-made special cases, including a star inspired by Faker. Each one pins only what makes them special; the generator fills in the rest ([world generation](../specs/world-generation.md)). Kairos is the exception: he pins every attribute that counts toward a mid's overall, so his overall is 96 in every world.

| Nickname | Name | Country | Role | Team | Born (age at start) | Pinned |
|---|---|---|---|---|---|---|
| Kairos | Han Do-yun | KR | Mid | Azure Tigers | 1997-03-14 (29) | Mechanics 95, Laning 96, Game Sense 97, Awareness 97, Positioning 95, Champion Pool Breadth 98, Shotcalling 96, Teamwork 95, Composure 96 (overall 96) |
| Faisca | Caio Ribeiro | BR | Bot | Onça Gaming | 2009-08-20 (17) | Potential 94 |
| Monsoon | Park Ji-hoon | KR | Support | Tempestade | 1998-11-02 (28) | Shotcalling 90, Teamwork 88, Mechanics 62 |
| Wildfire | Choi Min-jae | KR | Bot | Crimson Dynasty | 2004-05-09 (22) | Aggression 96, Consistency 25, Mechanics 88 |

- **Kairos** is the generational mid star, a veteran at the top of the strongest team, and the best player in the world.
- **Faisca** is the teenage prodigy: middling skills for now, with one of the highest ceilings in the world.
- **Monsoon** is the veteran import: a Korean shotcaller in Pindorama whose hands are slowing down.
- **Wildfire** is the volatile carry: brilliant mechanics and a hidden Consistency of 25.

The people's names are common names in their countries. They are chosen for not belonging to any well-known professional player.
