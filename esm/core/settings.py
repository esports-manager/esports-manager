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
from pathlib import Path

import yaml

from esm.definitions import *


class Settings:
    def __init__(self, root_dir: Path = ROOT_DIR):
        self.root_dir: Path = root_dir
        self.res_dir: Path = self.root_dir / "res"
        self.db_dir: Path = self.root_dir / "db"
        self.save_file_dir: Path = self.root_dir / "saves"
        self.logs_dir: Path = self.root_dir / "logs"

    @property
    def config_file(self) -> Path:
        return self.root_dir / "config.yaml"

    @property
    def definitions_dir(self) -> Path:
        return self.res_dir / "definitions"

    @property
    def names_file(self) -> Path:
        return self.definitions_dir / "names.json"

    @property
    def moba_definitions_dir(self) -> Path:
        return self.definitions_dir / "moba"

    @property
    def moba_champion_defs(self) -> Path:
        return self.moba_definitions_dir / "champions"

    @property
    def moba_championship_defs(self) -> Path:
        return self.moba_definitions_dir / "championships"

    @property
    def moba_team_defs(self) -> Path:
        return self.moba_definitions_dir / "teams"

    @property
    def db_moba_dir(self):
        return self.db_dir / "moba"

    @property
    def moba_region_defs(self) -> Path:
        return self.moba_team_defs / "regions.json"

    @property
    def moba_teams(self) -> Path:
        return self.db_moba_dir / "teams.json"

    @property
    def moba_regions(self) -> Path:
        return self.db_moba_dir / "regions.json"

    @property
    def moba_players(self) -> Path:
        return self.db_moba_dir / "players.json"

    @property
    def moba_champions(self) -> Path:
        return self.db_moba_dir / "champions.json"

    def load_config_file(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as fp:
                return yaml.safe_load(fp)
        else:
            self.create_config_file()

    def get_from_dict(self, data: dict[str, int | float | str]):
        self.root_dir = Path(data["root_dir"])
        self.res_dir = Path(data["res_dir"])
        self.db_dir = Path(data["db_dir"])
        self.save_file_dir = Path(data["save_file_dir"])
        self.logs_dir = Path(data["logs_dir"])

    def serialize(self) -> dict[str, int | float | str]:
        return {
            "root_dir": str(self.root_dir.absolute()),
            "res_dir": str(self.res_dir.absolute()),
            "db_dir": str(self.db_dir.absolute()),
            "save_file_dir": str(self.save_file_dir.absolute()),
            "logs_dir": str(self.logs_dir.absolute()),
        }

    def create_config_file(self):
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, "w") as fp:
            yaml.safe_dump(self.serialize(), fp)
