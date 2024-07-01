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
import uuid
from dataclasses import dataclass

from ...serializable import Serializable
from .mobaplayer import MobaPlayer, MobaPlayerSimulation


@dataclass
class MobaTeam(Serializable):
    team_id: uuid.UUID
    name: str
    nationality: str
    roster: list[MobaPlayer]

    def serialize(self) -> dict:
        players = [player.player_id.hex for player in self.roster]
        return {
            "team_id": self.team_id.hex,
            "name": self.name,
            "nationality": self.nationality,
            "roster": players,
        }

    @classmethod
    def get_from_dict(cls, dictionary: dict, players: list[MobaPlayer]):
        return cls(
            dictionary["team_id"],
            dictionary["name"],
            dictionary["nationality"],
            players,
        )


@dataclass
class TeamStats:
    kills: int = 0
    deaths: int = 0
    assists: int = 0


@dataclass
class MobaTowers:
    top: int = 3
    mid: int = 3
    bot: int = 3
    base: int = 2

    def reset(self):
        self.top = 3
        self.mid = 3
        self.bot = 3
        self.base = 2

    def all_down(self) -> bool:
        return self.top == 0 and self.mid == 0 and self.bot == 0 and self.base == 0

    def are_inhibs_exposed(self) -> bool:
        return self.top == 0 or self.mid == 0 or self.bot == 0

    def is_inhibitor_up(self, lane) -> bool:
        if lane == "top":
            return self.top != 0
        elif lane == "mid":
            return self.mid != 0
        elif lane == "bot":
            return self.bot != 0

    def get_exposed_inhibs(self) -> list[str]:
        exposed = []
        if self.top == 0:
            exposed.append("top")
        if self.mid == 0:
            exposed.append("mid")
        if self.bot == 0:
            exposed.append("bot")

        return exposed


class MobaTeamSimulation:
    def __init__(
        self, team: MobaTeam, players: list[MobaPlayerSimulation], is_players_team: bool
    ):
        self.team: MobaTeam = team
        self.towers: MobaTowers = MobaTowers()
        self.inhibitors: dict[str, int] = {
            "top": 1,
            "mid": 1,
            "bot": 1,
        }
        self.inhibitors_cooldown: dict[str, float] = {
            "top": 0.0,
            "mid": 0.0,
            "bot": 0.0,
        }
        self.is_players_team: bool = is_players_team
        self.players: list[MobaPlayerSimulation] = players
        self.stats: TeamStats = TeamStats()
        self.nexus: int = 1
        self.win_prob: float = 0.00
        self._player_overall: int = 0
        self._champion_overall: int = 0
        self._total_skill: int = 0
        self._points: int = 0

    def are_all_towers_down(self) -> bool:
        return self.towers.all_down()

    def is_inhibitor_up(self, lane: str) -> bool:
        return self.inhibitors[lane] != 0

    def are_all_inhibitors_up(self) -> bool:
        return 0 not in self.inhibitors.values()

    def are_inhibs_exposed(self) -> bool:
        return (
            self.towers["top"] == 0
            or self.towers["mid"] == 0
            or self.towers["bot"] == 0
        )

    def get_exposed_inhibs(self):
        return [
            lane
            for lane in self.towers.get_exposed_inhibs()
            if self.inhibitors[lane] != 0
        ]

    def is_nexus_exposed(self) -> bool:
        return self.towers.base == 0 and not self.are_all_inhibitors_up()

    def are_base_towers_exposed(self) -> bool:
        return not self.are_all_inhibitors_up()

    def get_players_default_lanes(self):
        for player in self.players:
            player.get_best_lane()

    def reset_values(self) -> None:
        for player in self.players:
            player.reset_attributes()

        self.towers.reset()
        self.inhibitors.update(
            {
                "top": 1,
                "mid": 1,
                "bot": 1,
            }
        )
        self.inhibitors_cooldown: dict[str, float] = {
            "top": 0.0,
            "mid": 0.0,
            "bot": 0.0,
        }

        self.win_prob = 0.0
        self.nexus = 1

    @property
    def kills(self) -> int:
        self.stats.kills = 0
        for player in self.players:
            self.stats.kills += player.stats.kills

        return self.stats.kills

    @property
    def deaths(self) -> int:
        self.stats.deaths = 0
        for player in self.players:
            self.stats.deaths += player.stats.deaths

        return self.stats.deaths

    @property
    def assists(self) -> int:
        self.stats.assists = 0
        for player in self.players:
            self.stats.assists += player.stats.assists

        return self.stats.assists

    @property
    def points(self) -> int:
        self._points = 0
        for player in self.players:
            self._points += player.points

        return self._points

    def get_team_overall(self) -> int:
        return int(sum(player.skill for player in self.players) / len(self.players))

    @property
    def player_overall(self) -> int:
        self._player_overall = sum(player.skill for player in self.players)

        return self._player_overall

    @property
    def champion_overall(self) -> int:
        self._champion_overall = int(
            sum(player.get_champion_skill() for player in self.players)
        )

        return self._champion_overall

    @property
    def total_skill(self) -> int:
        self._total_skill = (
            int(self.player_overall + self.champion_overall) + self.points
        )

        return int(self._total_skill)

    def __str__(self):
        return "{0}".format(self.team.name)

    def __repr__(self):
        return "{0} {1}".format(self.__class__.__name__, self.team.name)

    def __eq__(self, other):
        return (
            self.team.team_id == other.team.team_id
            if isinstance(other, MobaTeamSimulation)
            else NotImplemented
        )
