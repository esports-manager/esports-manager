-- SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
--
-- SPDX-License-Identifier: GPL-3.0-or-later

-- The first save schema: the world a New Game generates (saves spec).
-- Ids are the content's stable string ids. `position` keeps the order the
-- world was built in, so every query can order by it (ADR 0003).
--
-- Connections run with `foreign_keys = ON`, and Diesel runs each migration
-- in a transaction, where `PRAGMA foreign_keys = OFF` has no effect. A later
-- migration that rebuilds a table (create, copy, drop, rename) must set
-- `run_in_transaction = false` in its metadata.toml and switch foreign keys
-- off itself.

CREATE TABLE save_meta (
    id INTEGER PRIMARY KEY NOT NULL CHECK (id = 1),
    name TEXT NOT NULL,
    manager_name TEXT NOT NULL,
    team_id TEXT NOT NULL REFERENCES teams (id),
    genre TEXT NOT NULL CHECK (genre IN ('moba')),
    seed BIGINT NOT NULL,
    game_version TEXT NOT NULL,
    game_date TEXT NOT NULL,
    created_at BIGINT NOT NULL,
    last_played_at BIGINT NOT NULL
);

CREATE TABLE packages (
    id TEXT PRIMARY KEY NOT NULL,
    position INTEGER NOT NULL UNIQUE,
    version TEXT NOT NULL,
    content_hash BLOB NOT NULL CHECK (length(content_hash) = 32)
);

CREATE TABLE content_texts (
    locale TEXT NOT NULL,
    file TEXT NOT NULL,
    source TEXT NOT NULL,
    PRIMARY KEY (locale, file)
);

CREATE TABLE nationalities (
    id TEXT PRIMARY KEY NOT NULL,
    position INTEGER NOT NULL UNIQUE,
    code TEXT NOT NULL CHECK (length(code) = 2),
    name_order TEXT NOT NULL CHECK (name_order IN ('given_first', 'family_first'))
);

CREATE TABLE regions (
    id TEXT PRIMARY KEY NOT NULL,
    position INTEGER NOT NULL UNIQUE,
    level INTEGER NOT NULL
);

CREATE TABLE region_nationalities (
    region_id TEXT NOT NULL REFERENCES regions (id),
    nationality_id TEXT NOT NULL REFERENCES nationalities (id),
    weight INTEGER NOT NULL CHECK (weight >= 0),
    PRIMARY KEY (region_id, nationality_id)
);

CREATE TABLE teams (
    id TEXT PRIMARY KEY NOT NULL,
    position INTEGER NOT NULL UNIQUE,
    region_id TEXT NOT NULL REFERENCES regions (id),
    tag TEXT NOT NULL CHECK (length(tag) = 3),
    colour_fill TEXT NOT NULL CHECK (length(colour_fill) = 7),
    colour_border TEXT NOT NULL CHECK (length(colour_border) = 7),
    reputation INTEGER NOT NULL CHECK (reputation BETWEEN 1 AND 100)
);

CREATE TABLE competitions (
    id TEXT PRIMARY KEY NOT NULL,
    position INTEGER NOT NULL UNIQUE,
    region_id TEXT NOT NULL REFERENCES regions (id)
);

CREATE TABLE competition_teams (
    competition_id TEXT NOT NULL REFERENCES competitions (id),
    position INTEGER NOT NULL,
    team_id TEXT NOT NULL REFERENCES teams (id),
    PRIMARY KEY (competition_id, position)
);

CREATE TABLE roles (
    id TEXT PRIMARY KEY NOT NULL,
    position INTEGER NOT NULL UNIQUE,
    mechanics_weight INTEGER NOT NULL CHECK (mechanics_weight >= 0),
    laning_weight INTEGER NOT NULL CHECK (laning_weight >= 0),
    game_sense_weight INTEGER NOT NULL CHECK (game_sense_weight >= 0),
    awareness_weight INTEGER NOT NULL CHECK (awareness_weight >= 0),
    positioning_weight INTEGER NOT NULL CHECK (positioning_weight >= 0),
    champion_pool_breadth_weight INTEGER NOT NULL CHECK (champion_pool_breadth_weight >= 0),
    shotcalling_weight INTEGER NOT NULL CHECK (shotcalling_weight >= 0),
    teamwork_weight INTEGER NOT NULL CHECK (teamwork_weight >= 0),
    composure_weight INTEGER NOT NULL CHECK (composure_weight >= 0)
);

CREATE TABLE players (
    id TEXT PRIMARY KEY NOT NULL,
    position INTEGER NOT NULL UNIQUE,
    team_id TEXT NOT NULL REFERENCES teams (id),
    role_id TEXT NOT NULL REFERENCES roles (id),
    starter BOOLEAN NOT NULL,
    nickname TEXT NOT NULL,
    given_name TEXT NOT NULL,
    family_name TEXT NOT NULL,
    nationality_id TEXT NOT NULL REFERENCES nationalities (id),
    birth_date TEXT NOT NULL,
    mechanics INTEGER NOT NULL CHECK (mechanics BETWEEN 100 AND 9900),
    laning INTEGER NOT NULL CHECK (laning BETWEEN 100 AND 9900),
    game_sense INTEGER NOT NULL CHECK (game_sense BETWEEN 100 AND 9900),
    awareness INTEGER NOT NULL CHECK (awareness BETWEEN 100 AND 9900),
    positioning INTEGER NOT NULL CHECK (positioning BETWEEN 100 AND 9900),
    champion_pool_breadth INTEGER NOT NULL CHECK (champion_pool_breadth BETWEEN 100 AND 9900),
    shotcalling INTEGER NOT NULL CHECK (shotcalling BETWEEN 100 AND 9900),
    teamwork INTEGER NOT NULL CHECK (teamwork BETWEEN 100 AND 9900),
    aggression INTEGER NOT NULL CHECK (aggression BETWEEN 100 AND 9900),
    composure INTEGER NOT NULL CHECK (composure BETWEEN 100 AND 9900),
    work_ethic INTEGER NOT NULL CHECK (work_ethic BETWEEN 100 AND 9900),
    consistency INTEGER NOT NULL CHECK (consistency BETWEEN 100 AND 9900),
    potential INTEGER NOT NULL CHECK (potential BETWEEN 100 AND 9900)
);

CREATE INDEX players_by_team ON players (team_id, position);
