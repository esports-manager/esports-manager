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
import datetime
import uuid
from dataclasses import asdict, dataclass
from enum import Enum, auto

from ...serializable import Serializable
from ..player import Player
from .champion import Champion
from .moba_definitions import LaneError, LaneMultipliers, Lanes


@dataclass
class Attributes(Serializable):
    @classmethod
    def get_from_dict(cls, dictionary: dict[str, int]):
        return cls(**dictionary)

    def serialize(self) -> dict:
        return asdict(self)

    def get_overall(self) -> int:
        attrs = asdict(self)
        return int(sum(attrs.values()) / len(attrs))


@dataclass
class OffensiveAttributes(Attributes):
    lane_pressure: int
    kill_instinct: int
    aggressiveness: int


@dataclass
class CommunicationAttributes(Attributes):
    shot_calling: int
    decisioning: int
    team_work: int


@dataclass
class MechanicsAttributes(Attributes):
    reflexes: int
    speed: int
    farming: int
    kiting: int
    positioning: int
    accuracy: int


@dataclass
class UtilityAttributes(Attributes):
    vision_control: int
    map_control: int
    objective_control: int


@dataclass
class KnowledgeAttributes(Attributes):
    map_awareness: int
    timing: int
    itemization: int


@dataclass
class MobaPlayerAttributes(Serializable):
    offensive: OffensiveAttributes
    communication: CommunicationAttributes
    mechanics: MechanicsAttributes
    knowledge: KnowledgeAttributes
    utility: UtilityAttributes

    def get_overall(self, lane: Lanes) -> int:
        over_sum = (
            self.offensive.get_overall()
            + self.communication.get_overall()
            + self.mechanics.get_overall()
            + self.knowledge.get_overall()
            + self.utility.get_overall()
        )
        if lane in [Lanes.TOP, Lanes.MID]:
            over_sum += self.offensive.get_overall()
            over_sum += self.mechanics.get_overall()
            over_sum += self.communication.get_overall()
            over_sum += 2 * self.knowledge.get_overall()
        elif lane == Lanes.ADC:
            over_sum += self.offensive.get_overall()
            over_sum += 2 * self.mechanics.get_overall()
            over_sum += 2 * self.communication.get_overall()
        elif lane in [Lanes.JNG, Lanes.SUP]:
            over_sum += self.communication.get_overall()
            over_sum += self.knowledge.get_overall()
            over_sum += 3 * self.utility.get_overall()
        overall = over_sum / 10
        return int(overall)

    @classmethod
    def get_from_dict(cls, dictionary: dict[str, dict[str, int]]):
        return cls(
            OffensiveAttributes(**dictionary["offensive"]),
            CommunicationAttributes(**dictionary["communication"]),
            MechanicsAttributes(**dictionary["mechanics"]),
            KnowledgeAttributes(**dictionary["knowledge"]),
            UtilityAttributes(**dictionary["utility"]),
        )

    def serialize(self) -> dict:
        return {
            "offensive": self.offensive.serialize(),
            "communication": self.communication.serialize(),
            "mechanics": self.mechanics.serialize(),
            "knowledge": self.knowledge.serialize(),
            "utility": self.utility.serialize(),
        }


class ChampionMastery(Enum):
    BRONZE = auto()
    SILVER = auto()
    GOLD = auto()
    PLATINUM = auto()
    DIAMOND = auto()
    MASTER = auto()
    GRANDMASTER = auto()


@dataclass
class MobaPlayerChampion(Serializable):
    champion_id: uuid.UUID
    mastery: ChampionMastery
    total_exp: float

    @classmethod
    def get_from_dict(cls, dictionary: dict):
        return cls(
            uuid.UUID(hex=dictionary["champion_id"]),
            dictionary["mastery"],
            dictionary["total_exp"],
        )

    def serialize(self) -> dict:
        return {
            "champion_id": self.champion_id.hex,
            "mastery": self.mastery,
            "total_exp": self.total_exp,
        }


@dataclass
class MobaPlayer(Player, Serializable):
    lanes: LaneMultipliers
    attributes: MobaPlayerAttributes
    champion_pool: list[MobaPlayerChampion]

    @classmethod
    def get_from_dict(cls, dictionary: dict):
        return cls(
            uuid.UUID(dictionary["id"]),
            dictionary["nationality"],
            dictionary["first_name"],
            dictionary["last_name"],
            datetime.datetime.strptime(dictionary["birthday"], "%Y-%m-%d").date(),
            dictionary["nick_name"],
            LaneMultipliers.get_from_dict(dictionary["lanes"]),
            MobaPlayerAttributes.get_from_dict(dictionary["attributes"]),
            [
                MobaPlayerChampion.get_from_dict(champion)
                for champion in dictionary["champion_pool"]
            ],
        )

    def serialize(self) -> dict[str, int | str | float | dict | list]:
        return {
            "id": self.player_id.hex,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "birthday": "{:%Y-%m-%d}".format(self.birthday),
            "nick_name": self.nick_name,
            "nationality": self.nationality,
            "attributes": self.attributes.serialize(),
            "lanes": self.lanes.serialize(),
            "champion_pool": [champion.serialize() for champion in self.champion_pool],
        }

    def __repr__(self):
        return f"{self.__class__.__name__} {self.nick_name}"

    def __str__(self):
        return f"{self.nick_name}"


@dataclass
class MobaPlayerStats:
    kills: int = 0
    deaths: int = 0
    assists: int = 0
    max_consecutive_kills: int = 0
    max_kill_streak: int = 0

    def reset(self):
        self.kills = 0
        self.deaths = 0
        self.assists = 0
        self.max_consecutive_kills = 0
        self.max_kill_streak = 0


@dataclass
class MobaPlayerTeam:
    player_id: uuid.UUID
    team_id: uuid.UUID


@dataclass
class MobaPlayerSimulation:
    player: MobaPlayer
    champion: Champion
    lane: Lanes
    stats: MobaPlayerStats
    points: int = 0
    consecutive_kills: int = 0

    def reset_attributes(self) -> None:
        self.points = 0
        self.stats.reset()
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

        raise LaneError("Player may not be playing the game!")

    @property
    def skill(self) -> float:
        """
        Gets the player's skill according to the lane he is currently at.
        """
        return (
            self.player.attributes.get_overall(self.lane)
            * self.get_curr_lane_multiplier()
        )

    def get_projected_champion_skill(self, champion: Champion) -> float:
        """
        Gets a projected champion skill level, for champions that are not yet picked.
        """
        if champion is None:
            return 0

        mastery = ChampionMastery.BRONZE
        champion_ids = [ch.champion_id for ch in self.player.champion_pool]

        if champion.champion_id in champion_ids:
            for ch in self.player.champion_pool:
                if champion.champion_id == ch.champion_id:
                    mastery = ch.mastery
                    break

        # Default mastery for BRONZE mastery level
        mult = 1.0

        if mastery == ChampionMastery.SILVER:
            mult = 1.05
        elif mastery == ChampionMastery.GOLD:
            mult = 1.10
        elif mastery == ChampionMastery.PLATINUM:
            mult = 1.15
        elif mastery == ChampionMastery.DIAMOND:
            mult = 1.20
        elif mastery == ChampionMastery.MASTER:
            mult = 1.25
        elif mastery == ChampionMastery.GRANDMASTER:
            mult = 1.30

        return champion.skill * mult

    def get_champion_skill(self) -> float:
        """
        Gets the player_champion_skill according to the mastery level.
        """
        return self.get_projected_champion_skill(self.champion)

    @property
    def total_skill(self) -> float:
        """
        Gets the player + player_champion_skill + points to use in the match.
        This will define how strong or how weak a certain player is on the
        current match.
        """
        return self.skill + self.get_champion_skill() + self.points

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
