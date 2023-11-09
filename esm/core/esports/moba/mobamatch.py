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
from typing import Optional
from uuid import UUID
from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime

from esm.core.serializable import Serializable


class InvalidTeamId(Exception):
    pass


class MatchType(Enum):
    FRIENDLY = auto()
    PRACTICE = auto()
    SHOWMATCH = auto()
    LEAGUE = auto()
    PLAYOFFS = auto()
    FINALS = auto()


@dataclass
class MobaMatch(Serializable):
    game_id: UUID
    championship_id: UUID
    team1: UUID
    team2: UUID
    match_type: MatchType
    date: datetime
    victorious_team: Optional[UUID] = None

    def serialize(self) -> dict:
        if self.victorious_team is not None and self.victorious_team not in [self.team1, self.team2]:
            raise InvalidTeamId("Team cannot be the victorious team in this match!")

        victorious_team = UUID(hex=self.victorious_team) if self.victorious_team else None

        return {
            "game_id": self.game_id.hex,
            "championship_id": self.championship_id.hex,
            "team1": self.team1.hex,
            "team2": self.team2.hex,
            "match_type": self.match_type.value,
            "date": self.date.strftime("%Y-%m-%d, %H:%M"),
            "victorious_team": victorious_team,
        }

    @classmethod
    def get_from_dict(cls, dictionary: dict):
        victorious_team = dictionary["victorious_team"]
        team1 = dictionary["team1"]
        team2 = dictionary["team2"]

        if victorious_team is not None and victorious_team not in [team1, team2]:
            raise InvalidTeamId("Team cannot be the victorious team in this match!")
        else:
            victorious_team = UUID(hex=victorious_team)

        return cls(
            UUID(hex=dictionary["game_id"]),
            UUID(hex=dictionary["championship_id"]),
            UUID(hex=team1),
            UUID(hex=team2),
            MatchType(dictionary["match_type"]),
            datetime.strptime(dictionary["date"], "%Y-%m-%d, %H:%M"),
            victorious_team,
        )

    def __repr__(self) -> str:
        return "{0} {1}".format(self.__class__.__name__, self.game_id)

    def __str__(self) -> str:
        return "{0} ID: {1}".format(self.__class__.__name__, self.game_id)
