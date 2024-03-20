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
from typing import Tuple

from ..definitions import NAMES_FILE
from .esports.moba.generator import (
    ChampionGenerator,
    MobaPlayerGenerator,
    TeamGenerator,
)
from .esports.moba.mobateam import MobaTeam
from .gamestate import GameState
from .settings import Settings
from .utils import load_list_from_file


class DB:
    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def teams_file(self):
        return self.settings.teams_file

    @property
    def players_file(self):
        return self.settings.players_file

    @property
    def champions_file(self):
        return self.settings.champions_file

    def generate_moba_files(self) -> None:
        pass

    def load_moba_teams(self) -> list[MobaTeam]:
        pass

    def get_gamestate(self) -> GameState:
        pass

    def load_from_gamestate(self, gamestate: GameState):
        pass
