#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2022  Pedrenrique G. Guimarães
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
from datetime import datetime


class GameState:
    def __init__(self, gamename, filename, manager, season, esport, teams, players, champions):
        self.gamename = gamename
        self.filename = filename
        self.manager = manager
        self.season = season
        self.esport = esport
        self.teams = teams
        self.players = players
        self.champions = champions

    def get_data(self) -> dict:
        return {
            "filename": self.filename,
            "game_name": self.gamename,
            "manager": self.manager.get_dict(),
            "season": self.season,
            "esport": self.esport,
            "teams": self.teams.teams_dict,
            "champions": self.champions.champions_list,
            "players": self.players.players_dict,
            "save_date": datetime.now(),
        }
