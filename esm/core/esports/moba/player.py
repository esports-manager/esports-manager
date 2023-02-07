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
from datetime import date
from typing import Union
from dataclasses import dataclass

from .champion import Champion
from .moba_enums_def import Lanes, LaneError
from ..player import Player


@dataclass
class MobaPlayer(Player):
    mult: list[float]
    skill: int
    champions: list[dict]

    @classmethod
    def get_from_dict(cls, player: dict):
        return cls(
            uuid.UUID(int=player["id"]),
            player["nationality"],
            player["first_name"],
            player["last_name"],
            player["birthday"],
            player["nick_name"],
            player["multipliers"],
            player["skill"],
            player["champions"]
        )

    def get_dict(self) -> dict:
        return {
            "id": self.player_id.hex,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "birthday": "{:%Y/%m/%d}".format(self.birthday),
            "nick_name": self.nick_name,
            "nationality": self.nationality,
            "skill": self.skill,
            "multipliers": self.mult,
            "champions": self.champions.copy(),
        }

    def __repr__(self):
        return "{self.__class__.__name__} {self.nick_name}".format(self.__class__.__name__, self.nick_name)

    def __str__(self):
        return f"{self.nick_name}"

@dataclass
class MobaPlayerSimulator:
    player: MobaPlayer
    champion: Champion
    lane: Lanes
    kills: int = 0
    deaths: int = 0
    assists: int = 0
    points: int = 0
    consecutive_kills: int = 0

    def reset_attributes(self) -> None:
        self.points = 0
        self.kills = 0
        self.deaths = 0
        self.assists = 0
        self.consecutive_kills = 0

    def get_highest_multiplier(self) -> float:
        """
        Gets the highest lane multiplier.
        """
        return max(self.player.mult)

    def get_best_lane(self) -> int:
        """
        Gets the highest lane multiplier, the lane that the player is 100% confident on playing.
        """
        return self.player.mult.index(self.get_highest_multiplier())

    def get_default_lane(self) -> None:
        """
        Gets the best lane for the player, and assigns him to it.
        This will be useful for default picks and bans, and is used for debugging as well.
        """
        lane = self.get_best_lane()
        self.lane = lane

    def get_curr_lane_multiplier(self) -> int:
        """
        Gets the current lane multiplier in-game, this will define how good a player is on that particular lane.

        Each player has at least one lane where he is 100% confident to play on.
        """
        if self.lane is not None:
            return self.player.mult[self.lane.value]
        else:
            raise LaneError("Player may not be playing the game!")

    def get_curr_player_skill(self) -> float:
        """
        Gets the player's skill according to the lane he is currently at.
        """
        return self.player.skill * self.get_curr_lane_multiplier()

    def get_projected_champion_skill(self, champion: Champion) -> float:
        """
        Gets a projected champion skill level, for champions that are not yet picked.
        """
        if champion is None:
            return 0
        mult = next(
            (
                ch["mult"]
                for ch in self.player.champions
                if ch["id"] == champion.champion_id.hex
            ),
            0.5,
        )

        return (0.5 * champion.skill) * (1 + mult)

    def get_champion_skill(self) -> float:
        """
        Gets the player_champion_skill according to the multiplier.
        If for some reason a champion is not on the list, it receives a default multiplier of 0.5.
        """
        return self.get_projected_champion_skill(self.champion)

    def get_player_total_skill(self) -> float:
        """
        Gets the player + player_champion_skill + points to use in the match.
        This will define how strong or how weak a certain player is on the current match.
        """
        return (
            self.get_curr_player_skill() + self.get_champion_skill()
        ) / 2 + self.points

    def is_player_on_killing_spree(self) -> bool:
        """
        Returns true if the player is on killing spree. False otherwise.
        """
        return 2 <= self.consecutive_kills <= 4

    def is_player_godlike(self) -> bool:
        """
        Returns true if the player is godlike. False otherwise.
        """
        return 4 < self.consecutive_kills < 8

    def is_player_legendary(self):
        """
        Returns true if the player is legendary. False otherwise.
        """
        return self.consecutive_kills >= 8