#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2023  Pedrenrique G. Guimarães
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
import os.path
from dataclasses import dataclass
from pathlib import Path
from typing import Union

import yaml

from esm.definitions import *


@dataclass
class Settings:
    font_scale: int = 1
    amount_players: int = 50
    enable_auto_save = True
    root_dir: Union[str, Path] = ROOT_DIR
    res_dir: Union[str, Path] = RES_DIR
    db_dir: Union[str, Path] = DB_DIR
    save_file_dir: Union[str, Path] = SAVE_FILE_DIR
    champions_file: Union[str, Path] = CHAMPIONS_FILE
    players_file: Union[str, Path] = PLAYERS_FILE
    teams_file: Union[str, Path] = TEAMS_FILE
    config_file: Union[str, Path] = CONFIG_FILE

    def load_config_file(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as fp:
                return yaml.safe_load(fp)
        else:
            self.create_config_file()

    def parse_config_file(self, data):
        self.font_scale = data['font_scale']
        self.amount_players = data['amount_players']
        self.enable_auto_save = data['enable_auto_save']
        self.root_dir = data['root_dir']
        self.res_dir = data['res_dir']
        self.db_dir = data['db_dir']
        self.save_file_dir = data['save_file_dir']
        self.champions_file = data['champions_file']
        self.players_file = data['players_file']
        self.teams_file = data['teams_file']

    def get_data(self):
        return {
            "font_scale": self.font_scale,
            "amount_players": self.amount_players,
            "root_dir": str(self.root_dir),
            "enable_auto_save": str(self.enable_auto_save),
            "res_dir": str(self.res_dir),
            "db_dir": str(self.db_dir),
            "save_file_dir": str(self.save_file_dir),
            "champions_file": str(self.champions_file),
            "players_file": str(self.players_file),
            "teams_file": str(self.teams_file),
        }

    def create_config_file(self):
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as fp:
            yaml.safe_dump(self.get_data(), fp)
