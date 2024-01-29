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

import random
import uuid
from typing import Optional

from esm.core.esports.moba.generator.default_team_names import get_default_team_names
from esm.core.esports.moba.generator.generate_players import MobaPlayerGenerator
from esm.core.esports.moba.generator.generator import GeneratorInterface
from esm.core.esports.moba.player import MobaPlayer
from esm.core.esports.moba.team import Team
from esm.definitions import TEAMS_FILE


class TeamGeneratorError(Exception):
    pass


class TeamGenerator(GeneratorInterface):
    def __init__(
        self,
        players: Optional[list] = None,
    ):
        self.player_list = players

    def generate_id(self) -> uuid.UUID:
        """
        Generates teams UUID
        """
        return uuid.uuid4()

    def generate_roster(self) -> None:
        """
        Generates the team roster
        """
        if self.player_list is None or self.player_list == []:
            raise TeamGeneratorError("Player roster is invalid!")

    def generate(self) -> Team:
        """
        Generates the team
        """
        if self.player_list is None or self.player_list == []:
            raise TeamGeneratorError("Player roster is invalid!")
