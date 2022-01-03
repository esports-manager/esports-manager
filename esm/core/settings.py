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
import os
import yaml

from esm.definitions import *
from dataclasses import dataclass


@dataclass
class Settings:
    font_scale: int = 1
    res_dir: str = RES_DIR
    db_dir: str = DB_DIR
    save_file_dir: str = SAVE_FILE_DIR
    champions_file: str = CHAMPIONS_FILE
    players_file: str = PLAYERS_FILE
    teams_file: str = TEAMS_FILE
    config_file: str = CONFIG_FILE

    def load_config_file(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as fp:
                return yaml.safe_load(fp)
        else:
            self.create_config_file()

    def parse_config_file(self, data):
        pass

    def get_data(self):
        return {
            "font_scale": self.font_scale,
            "res_dir": self.res_dir,
            "db_dir": self.db_dir,
            "save_file_dir": self.save_file_dir,
            "champions_file": self.champions_file,
            "players_file": self.players_file,
            "teams_file": self.teams_file,
        }

    def create_config_file(self):
        with open(self.config_file, 'w') as fp:
            yaml.safe_dump(self.get_data(), fp)
