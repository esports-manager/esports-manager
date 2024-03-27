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
from esm.core.esports.moba.generator.generate_champions import Champion
from esm.core.esports.moba.generator.generate_players import MobaPlayerGenerator
from esm.core.esports.moba.generator.generator import GeneratorInterface
from esm.core.esports.moba.mobateam import MobaTeam
from esm.core.esports.moba.player import Lanes, MobaPlayer


class TeamGeneratorError(Exception):
    pass


class TeamGenerator(GeneratorInterface):
    def __init__(
        self,
        champions: list[Champion],
        player_names: list[dict[str, str | float]],
        players: Optional[list] = None,
    ):
        self.player_list = players
        if not champions:
            raise TeamGeneratorError("Champion list is empty")
        self.player_gen = MobaPlayerGenerator(champions, player_names)

    @staticmethod
    def generate_id() -> uuid.UUID:
        """
        Generates teams UUID
        """
        return uuid.uuid4()

    @staticmethod
    def generate_name() -> str:
        return random.choice(get_default_team_names())

    def generate_roster(
        self, nationality: str, mu: int, sigma: int
    ) -> list[MobaPlayer]:
        """
        Generates the team roster
        """
        if self.player_list:
            return self.player_list

        return [
            self.player_gen.generate(
                lane=lane, nationality=nationality, mu=mu, sigma=sigma
            )
            for lane in list(Lanes)
        ]

    def generate(self, team_definition: dict[str, str | int]) -> MobaTeam:
        """
        Generates the team
        """
        nationality = team_definition["nationality"]
        mu = team_definition["mu"]
        sigma = team_definition["sigma"]
        return MobaTeam(
            team_id=self.generate_id(),
            name=team_definition["name"],
            nationality=nationality,
            roster=self.generate_roster(nationality, mu, sigma),
        )
