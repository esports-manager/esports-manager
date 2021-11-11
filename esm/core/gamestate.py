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
import cbor2
from tempfile import NamedTemporaryFile


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
        self.temporary_file = None
        
    def create_temporary_file(self):
        """
        Creates the temporary file as a backup for savefile
        """
        self.temporary_file = NamedTemporaryFile()

    def normalize_data(self) -> dict:
        return {
            "filename": self.filename,
            "game_name": self.gamename,
            "manager": self.manager.get_dict(),
            "season": self.season,
            "esport": self.esport,
            "teams": self.teams.teams_dict,
            "champions": self.champions.champions_list,
            "players": self.players.players_dict,
        }

    def write_to_temporary_file(self):
        if self.temporary_file is None:
            self.create_temporary_file()
        with open(self.temporary_file) as fp:
            cbor2.dump(self.normalize_data(), fp)
