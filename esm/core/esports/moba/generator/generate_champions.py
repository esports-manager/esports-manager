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

import random
import uuid
from pathlib import Path
from typing import Union

from esm.core.utils import load_list_from_file
from .default_champion_defs import get_default_champion_names
from .generator import GeneratorInterface
from ..champion import Champion


class ChampionGenerator(GeneratorInterface):
    def __init__(self, champion_def: Path):
        self.champion_def = load_list_from_file(champion_def)

    def generate_champion_id(self) -> uuid.UUID:
        """
        Generates champion UUID
        """
        return uuid.uuid4()

    def generate_champion_lanes(self) -> None:
        pass

    def generate(self) -> list[Champion]:
        pass