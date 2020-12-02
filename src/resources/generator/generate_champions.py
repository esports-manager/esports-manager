#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020  Pedrenrique G. Guimarães
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

from src.resources.utils import write_to_json, get_list_from_file
from src.core.esports.moba.champion import Champion


class ChampionGenerator:
    def __init__(self,
                 name: str = None,
                 skill: int = None,
                 lane: str = None,
                 champion_dict: dict = None,
                 file_name: str = 'champions.json',
                 champion_obj: Champion = None,
                 champion_names: list = None
                 ):
        self.name = name
        self.skill = skill
        self.lane = lane
        self.file_name = file_name
        self.champion_dict = champion_dict
        self.champion_obj = champion_obj
        self.champion_names = champion_names
        self.champions_list = []
        self.champions_obj = []

    def get_champion_names(self):
        self.champion_names = get_list_from_file(self.file_name)

    def get_champion_lanes(self):
        pass

    def generate_champion_dict(self, champion_name: str, counter: int):
        if champion_name == "TEEMO":
            skill = random.randint(0, 50)
        else:
            skill = random.randint(50, 99)

        self.champion_dict = {"name": champion_name,
                              "id": counter,
                              "skill": skill
                              }

    def create_champions_list(self):
        for counter, champion_name in enumerate(self.champion_names):
            self.generate_champion_dict(champion_name, counter)
            self.champions_list.append(self.champion_dict)

    def generate_file(self) -> None:
        write_to_json(self.champions_list, self.file_name)
