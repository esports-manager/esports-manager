#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2021  Pedrenrique G. Guimarães
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
from esm.resources import RES

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
RES_DIR = RES
DB_DIR = os.path.join(RES, "db")
SAVE_FILE_DIR = os.path.join(RES, "save")
CHAMPIONS_FILE = "champions.json"
PLAYERS_FILE = "players.json"
TEAMS_FILE = "teams.json"
DEBUG = True
