#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2024  Pedrenrique G. Guimarães
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os

ROOT_DIR = os.path.dirname(os.path.abspath(os.curdir))
RES_DIR = os.path.join(ROOT_DIR, "res")
DB_DIR = os.path.join(RES_DIR, "db")
SAVE_FILE_DIR = os.path.join(RES_DIR, "save")
MOBA_DEFINITIONS_DIR = os.path.join(DB_DIR, "moba", "definitions")
MOBA_CHAMPION_DEFINITIONS = os.path.join(MOBA_DEFINITIONS_DIR, "champions")
MOBA_TEAM_DEFINITIONS = os.path.join(MOBA_DEFINITIONS_DIR, "teams")
MOBA_CHAMPIONSHIP_DEFINITIONS = os.path.join(MOBA_DEFINITIONS_DIR, "championships")
MOBA_REGION_DEFINITIONS = os.path.join(MOBA_DEFINITIONS_DIR, "teams", "regions.json")
MOBA_TEAMS = os.path.join(DB_DIR, "moba", "teams.json")
MOBA_CHAMPIONS = os.path.join(DB_DIR, "moba", "champions.json")
MOBA_PLAYERS = os.path.join(DB_DIR, "moba", "players.json")
MOBA_REGIONS = os.path.join(DB_DIR, "moba", "regions.json")
NAMES_FILE = os.path.join(DB_DIR, "names.json")
CONFIG_FILE = os.path.join(ROOT_DIR, "config.yaml")
LOG_FILE = os.path.join(ROOT_DIR, "logs", "esm.log")
DEBUG = True
