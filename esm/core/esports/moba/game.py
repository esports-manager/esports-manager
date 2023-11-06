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
from typing import Union
from uuid import UUID

from esm.core.esports.moba.player import MobaPlayerSimulation
from esm.core.esports.moba.team import Team, TeamSimulation
from esm.core.serializable import Serializable


class Game(Serializable):
    """
    The Match class is used to represent a match, whether they include
    the user's team or not.
    """

    def __init__(
            self,
            game_id: Union[UUID, int],
            championship_id: Union[UUID, int],
            team1: TeamSimulation,
            team2: TeamSimulation,
    ):
        """
        Initializes elements of the match
        :param game_id: match ID
        :param championship_id: championship ID to which the match belongs
        :param team1: first team (blue side/radiant)
        :param team2: second team (red side/dire)
        """
        self.game_id = game_id
        self.championship_id = championship_id
        self.team1 = team1
        self.team2 = team2
        self.teams = [self.team1, self.team2]
        self.victorious_team = None

    def serialize(self) -> dict:
        victorious_team = self.victorious_team.team_id.hex if self.victorious_team else None

        return {
            "game_id": self.game_id.hex,
            "championship_id": self.championship_id.hex,
            "team1": self.team1.team.team_id.hex,
            "team2": self.team2.team.team_id.hex,
            "victorious_team": victorious_team
        }

    @classmethod
    def get_from_dict(cls, dictionary: dict, teams: list[Team], players: list[MobaPlayer]):
        for team in teams:
            if team.team_id == dictionary["team1"]:
                team1 = TeamSimulation(team, )

        return cls(

        )

    def __repr__(self) -> str:
        return "{0} {1}".format(self.__class__.__name__, self.game_id)

    def __str__(self) -> str:
        return "{0} ID: {1}".format(self.__class__.__name__, self.game_id)