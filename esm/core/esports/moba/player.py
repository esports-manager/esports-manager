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
from dataclasses import dataclass, asdict

from .champion import Champion
from .moba_enums_def import Lanes, LaneError, LaneMultipliers
from ..player import Player
from ...serializable import Serializable


@dataclass
class MobaPlayerAttributes(Serializable):
    aggressiveness: int
    mechanics: int
    awareness: int
    knowledge: int
    reflexes: int
    positioning: int
    timing: int
    cs: int

    def get_skill_from_lane(self, lane: Lanes) -> int:
        if lane == Lanes.TOP or lane == Lanes.MID or lane == Lanes.ADC:
            skill = int((self.aggressiveness + self.mechanics + self.awareness + self.knowledge + self.reflexes + self.positioning + self.cs + self.timing) / 8)
        else:
            skill = int((self.aggressiveness + self.mechanics + self.awareness + self.knowledge + self.reflexes + self.positioning + self.timing) / 7)

        return skill

    @classmethod
    def get_from_dict(cls, attributes: dict[str, int]):
        return cls(
            attributes["agressiveness"],
            attributes["mechanics"],
            attributes["awareness"],
            attributes["knowledge"],
            attributes["reflexes"],
            attributes["positioning"],
            attributes["timing"],
            attributes["cs"],
        )

    def serialize(self) -> dict:
        return asdict(self)


@dataclass
class MobaPlayer(Player, Serializable):
    lanes: LaneMultipliers
    attributes: MobaPlayerAttributes
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
            player["attributes"],
            LaneMultipliers.get_from_dict(player["multipliers"]),
            player["champions"]
        )

    def serialize(self) -> dict[str, int | str | float | dict | list]:
        return {
            "id": self.player_id.hex,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "birthday": "{:%Y/%m/%d}".format(self.birthday),
            "nick_name": self.nick_name,
            "nationality": self.nationality,
            "attributes": self.attributes.serialize(),
            "lanes": self.lanes.serialize(),
            "champions": self.champions.copy(),
        }

    def __repr__(self):
        return f"{self.__class__.__name__} {self.nick_name}"

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
        lanes = self.player.lanes.serialize()
        return max(lanes.values())

    def get_best_lane(self) -> Lanes:
        """
        Gets the highest lane multiplier, the lane that the player is 100% confident on playing.
        """
        return self.player.lanes.get_best_attribute()

    def get_curr_lane_multiplier(self) -> float:
        """
        Gets the current lane multiplier in-game, this will define how good a player is on that particular lane.

        Each player has at least one lane where he is 100% confident to play on.
        """
        if self.lane is not None:
            return self.player.lanes[self.lane]
        else:
            raise LaneError("Player may not be playing the game!")

    @property
    def skill(self) -> float:
        """
        Gets the player's skill according to the lane he is currently at.
        """
        return self.player.attributes.get_skill_from_lane(self.lane) * self.get_curr_lane_multiplier()

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

    @property
    def total_skill(self) -> float:
        """
        Gets the player + player_champion_skill + points to use in the match.
        This will define how strong or how weak a certain player is on the current match.
        """
        return (
                self.skill + self.get_champion_skill()
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
