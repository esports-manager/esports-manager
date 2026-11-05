<!--
SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
SPDX-License-Identifier: GPL-3.0-or-later
License-Filename: LICENSES/GPL-3.0-or-later
-->

# Games and BGMI tournaments

eSports Manager is no longer tied to a single title. A **game registry** describes
the eSports available in a save and each tournament belongs to a game. Two games
are registered automatically on first start:

| Game | Slug | Genre | Tournament system |
| --- | --- | --- | --- |
| League of Legends | `league-of-legends` | `moba` | MOBA series |
| BGMI (Battlegrounds Mobile India) | `bgmi` | `battle_royale` | BGMI battle royale |

The game genre selects the tournament ruleset:

- `moba` → MOBA tournaments (`moba_tournaments`, best-of series, brackets).
- `battle_royale` → BGMI tournaments (`bgmi_tournaments`, placement + kill points).
- Any other genre (`fps`, `rts`, ...) can be registered in the games list, but it
  has no tournament format yet. Registering it now means its data is ready for a
  future format module.

## BGMI scoring

BGMI tournaments store their own scoring rules so different events can use
different tables:

| Field | Default | Meaning |
| --- | --- | --- |
| `game_mode` | `squad` | `solo`, `duo` or `squad` |
| `map_pool` | `erangel, miramar, sanhok, vikendi` | Maps used by the event |
| `points_per_kill` | `1` | Points awarded per elimination |
| `placement_points` | `{"1": 10, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 1}` | Points per finishing position |
| `teams_per_lobby` | `16` | Teams expected per match |
| `match_count` | `6` | Matches in the series |

Every other field (`name`, `type`, `format`, `tier`, `status`, dates, location,
banner, colour, logo) is shared with MOBA tournaments.

## API

All endpoints are served under `/api`. Valid tournament filter values are the
enum **values** (`single_elimination`, `premier`, ...), names are accepted too.

### Games

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/games` | List games. Filters: `genre`, `tournament_system`, `active`, `search` |
| `POST` | `/api/games` | Register a game. `409` when the name or slug already exists |
| `GET` | `/api/games/{id}` | Fetch a game |
| `GET` | `/api/games/by-slug/{slug}` | Fetch a game by slug |
| `PATCH` | `/api/games/{id}` | Update a game |
| `DELETE` | `/api/games/{id}` | Delete a game (`409` while it still has tournaments) |

`POST /api/games` body:

```json
{
  "name": "VALORANT",
  "slug": "valorant",
  "abbreviation": "VAL",
  "genre": "fps",
  "publisher": "Riot Games",
  "platform": "PC",
  "team_size": 5,
  "description": "Tactical five-versus-five shooter."
}
```

`slug` is optional and derived from the name when omitted. `genre` is required and
must be one of `moba`, `battle_royale`, `fps`, `rts`, `sports`, `fighting`,
`other`.

### BGMI tournaments

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/bgmi/tournaments` | List BGMI tournaments |
| `POST` | `/api/bgmi/tournaments` | Create a BGMI tournament |
| `GET` | `/api/bgmi/tournaments/{id}` | Fetch a tournament |
| `PATCH` | `/api/bgmi/tournaments/{id}` | Update a tournament |
| `DELETE` | `/api/bgmi/tournaments/{id}` | Delete a tournament and its registrations |
| `GET` | `/api/bgmi/tournaments/{id}/teams` | Participating teams |
| `POST` | `/api/bgmi/tournaments/{id}/teams` | Register a team (`{"team_id": 1}`) |
| `DELETE` | `/api/bgmi/tournaments/{id}/teams/{team_id}` | Remove a team |

Listing filters: `game_mode`, `tier`, `type`, `format`, `status`, `location`,
`search`, `sort` (`name`, `start_date`, `end_date`, `tier`), `direction`
(`asc`/`desc`), `page` and `per_page` (max 100).

Creating a tournament:

```bash
curl -X POST http://localhost:8000/api/bgmi/tournaments \
  -H "Content-Type: application/json" \
  -d '{
        "name": "Battlegrounds Mobile India Series 2025",
        "abbreviation": "BGIS 2025",
        "type": "national",
        "format": "league",
        "tier": "major",
        "start_date": "2025-07-01",
        "end_date": "2025-08-15",
        "location": "India",
        "game_mode": "squad",
        "map_pool": ["erangel", "miramar", "sanhok"],
        "points_per_kill": 2,
        "teams_per_lobby": 25,
        "match_count": 8
      }'
```

`game_id` is optional: when omitted the tournament is attached to the oldest
active battle royale game (BGMI on a fresh install). Passing a game that is not a
battle royale title returns `400`; an unknown `game_id` returns `404`.

Teams are read from the existing team registry, so any team created through
`/api/moba/teams` can play a BGMI tournament. A game agnostic team model is
planned in [FEATURES.md](../FEATURES.md); until then BGMI registrations point at
`moba_teams`.

### Unified listing

`GET /api/tournaments` merges MOBA and BGMI tournaments into one list. Use
`?game=bgmi` (or any registered slug) to scope it to a single title; an unknown
slug returns an empty list. Filtering, sorting and pagination work as above.

Every listing endpoint returns the same summary shape:

```json
{
  "id": 1,
  "name": "Battlegrounds Mobile India Series 2025",
  "type": "national",
  "format": "league",
  "tier": "major",
  "status": "not_started",
  "start_date": "2025-07-01",
  "end_date": "2025-08-15",
  "location": "India",
  "game_id": 2,
  "game_slug": "bgmi",
  "game_name": "BGMI",
  "system": "bgmi",
  "url": "/tournaments/bgmi/1",
  "images_url": "/api/bgmi/tournaments/images/"
}
```

## Frontend

- **Games** (`/page/games`) lists the registry and lets you add a game. A game
  whose genre has no ruleset shows *No tournament format yet*.
- **Tournaments** (`/page/tournaments`) merges every game, can be filtered per
  game, and the **New Tournament** dialog adapts to the selected game: choosing
  BGMI reveals the battle royale fields.
- **BGMI detail** (`/tournaments/bgmi/{id}`) shows scoring, map pool, lobby size
  and participating teams, and allows registering teams.

## Adding another game

Games are data, not code: `POST /api/games` (or the **Add Game** dialog) is
enough to make a MOBA or battle royale title create tournaments immediately. A
new *format* (for example CS2 or Dota) needs a tournament model and routes next
to `esm/models/bgmi` and `esm/routes/bgmi`; register the mapping in
`GAME_TOURNAMENT_SYSTEM` (`esm/models/game.py`) and the API and UI pick it up.

## Database notes

Tables are created on startup. Databases created before the game registry existed
get the new `moba_tournaments.game_id` column added automatically by
`DatabaseManager._upgrade_legacy_schema`, so existing saves keep working.
