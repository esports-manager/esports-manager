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
import os.path
from dataclasses import dataclass
from pathlib import Path
from typing import Union

import yaml

from esm.definitions import *


@dataclass
class Settings:
    font_scale: int = 1
    enable_auto_save = True
    root_dir: Union[str, Path] = ROOT_DIR
    res_dir: Union[str, Path] = RES_DIR
    db_dir: Union[str, Path] = DB_DIR
    save_file_dir: Union[str, Path] = SAVE_FILE_DIR
    moba_team_defs: Union[str, Path] = MOBA_TEAM_DEFINITIONS
    moba_championship_defs: Union[str, Path] = MOBA_CHAMPIONSHIP_DEFINITIONS
    moba_champion_defs: Union[str, Path] = MOBA_CHAMPION_DEFINITIONS
    moba_region_defs: Union[str, Path] = MOBA_REGION_DEFINITIONS
    moba_teams: Union[str, Path] = MOBA_TEAMS
    moba_champions: Union[str, Path] = MOBA_CHAMPIONS
    moba_players: Union[str, Path] = MOBA_PLAYERS
    moba_regions: Union[str, Path] = MOBA_REGIONS
    names_file: Union[str, Path] = NAMES_FILE
    config_file: Union[str, Path] = CONFIG_FILE

    def load_config_file(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as fp:
                return yaml.safe_load(fp)
        else:
            self.create_config_file()

    def get_from_dict(self, data: dict[str, int | float | str]):
        self.font_scale = data["font_scale"]
        self.enable_auto_save = data["enable_auto_save"]
        self.root_dir = data["root_dir"]
        self.res_dir = data["res_dir"]
        self.db_dir = data["db_dir"]
        self.moba_team_defs = data["moba_team_defs"]
        self.moba_championship_defs = data["moba_championship_defs"]
        self.moba_champion_defs = data["moba_champion_defs"]
        self.moba_teams = data["moba_teams"]
        self.moba_champions = data["moba_champions"]
        self.moba_players = data["moba_players"]
        self.moba_regions = data["moba_regions"]
        self.names_file = data["names_file"]
        self.save_file_dir = data["save_file_dir"]

    def serialize(self) -> dict[str, int | float | str]:
        return {
            "font_scale": self.font_scale,
            "root_dir": str(self.root_dir),
            "enable_auto_save": str(self.enable_auto_save),
            "res_dir": str(self.res_dir),
            "db_dir": str(self.db_dir),
            "moba_team_defs": str(self.moba_team_defs),
            "moba_championship_defs": str(self.moba_championship_defs),
            "moba_teams": str(self.moba_teams),
            "moba_champions": str(self.moba_champions),
            "moba_players": str(self.moba_players),
            "moba_regions": str(self.moba_regions),
            "save_file_dir": str(self.save_file_dir),
        }

    def create_config_file(self):
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, "w") as fp:
            yaml.safe_dump(self.serialize(), fp)
