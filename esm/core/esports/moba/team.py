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
import uuid
from typing import Union


class Team:
    def __init__(
            self,
            team_id: Union[int, uuid.UUID],
            name: str,
            list_players,
            is_players_team=False
    ):
        """
        Initiates the team object.
        """
        self._points = 0
        if isinstance(team_id, int):
            self.team_id = uuid.UUID(int=team_id)
        elif isinstance(team_id, uuid.UUID):
            self.team_id = team_id
        self.name = name

        # MATCH RELATED
        self.towers = {"top": 3, "mid": 3, "bot": 3, "base": 2}
        self.inhibitors = {"top": 1, "mid": 1, "bot": 1}

        self.is_players_team = is_players_team  # Checks if the user is controlling the team

        self.nexus = 1

        self.win_prob = 0.00

        self.list_players = list_players

        self._kills = 0
        self._deaths = 0
        self._assists = 0

        self._player_overall = 0
        self._champion_overall = 0
        self._total_skill = 0

        self._bans = []

    def is_tower_up(self, lane: str) -> bool:
        return self.towers[lane] != 0

    def are_all_towers_up(self) -> bool:
        return 0 not in self.towers.values()

    def are_all_towers_down(self) -> bool:
        return (
                self.towers["top"] == 0
                and self.towers["mid"] == 0
                and self.towers["bot"] == 0
                and self.towers["base"] == 0
        )

    def are_all_lane_towers_down(self) -> bool:
        return (
                self.towers["top"] == 0
                and self.towers["mid"] == 0
                and self.towers["bot"] == 0
        )

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
            for lane, num in self.towers.items()
            if num == 0 and lane != "base" and self.inhibitors[lane] != 0
        ]

    def is_nexus_exposed(self) -> bool:
        return self.towers["base"] == 0 and not self.are_all_inhibitors_up()

    def are_base_towers_exposed(self) -> bool:
        return not self.are_all_inhibitors_up()

    def get_players_default_lanes(self):
        for player in self.list_players:
            player.get_default_lane()

    def reset_values(self) -> None:
        for player in self.list_players:
            player.reset_attributes()

        self._bans.clear()

        self.towers.update(
            {
                "top": 3,
                "mid": 3,
                "bot": 3,
                "base": 2,
            }
        )

        self.inhibitors.update(
            {
                "top": 1,
                "mid": 1,
                "bot": 1,
            }
        )

        self.win_prob = 0
        self.nexus = 1

    @property
    def bans(self) -> list:
        return self._bans

    @bans.setter
    def bans(self, champion) -> None:
        self._bans.append(champion)

    @property
    def kills(self) -> int:
        self._kills = 0
        for player in self.list_players:
            self._kills += player.kills

        return self._kills

    @property
    def deaths(self) -> int:
        self._deaths = 0
        for player in self.list_players:
            self._deaths += player.deaths

        return self._deaths

    @property
    def assists(self) -> int:
        self._assists = 0
        for player in self.list_players:
            self._assists += player.assists

        return self._assists

    @property
    def points(self) -> int:
        self._points = 0
        for player in self.list_players:
            self._points += player.points

        return self._points

    def get_team_overall(self) -> int:
        return int(sum(
            player.skill for player in self.list_players
        ) / len(self.list_players))

    @property
    def player_overall(self) -> int:
        """
        This method is calculating team's overall
        :return:
        """
        self._player_overall = sum(
            player.get_curr_player_skill() for player in self.list_players
        )

        return self._player_overall

    @property
    def champion_overall(self) -> int:
        self._champion_overall = int(
            sum(player.get_champion_skill() for player in self.list_players)
        )

        return self._champion_overall

    @property
    def total_skill(self) -> int:
        self._total_skill = ((self.player_overall + self.champion_overall) / 10) + self.points

        return int(self._total_skill)

    @classmethod
    def get_from_dict(cls, team: dict):
        return cls(
            team["id"],
            team["name"],
            team["roster"],
        )

    def __str__(self):
        return "{0}".format(self.name)

    def __repr__(self):
        return "{0} {1}".format(self.__class__.__name__, self.name)

    def __eq__(self, other):
        return self.team_id == other.team_id if isinstance(other, Team) else NotImplemented
