#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2021  Pedrenrique G. Guimarães
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
from datetime import date

from esm.core.esports.moba.moba_enums_def import Lanes, LaneError
from esm.core.esports.moba.champion import Champion
from esm.core.esports.player import Player


class MobaPlayer(Player):
    """
    The MobaPlayer class defines a MobaPlayer and contains all info that are relevant for in-game calculations
    and all other player info. The player is generated by the MobaPlayerGenerator, and can also be retrieved
    from the database using the MobaPlayerGenerator.
    """

    def __init__(
        self,
        player_id: int,
        nationality: str,
        first_name: str,
        last_name: str,
        birthday: date,
        nick_name: str,
        mult: list,
        skill: int,
        champions: list,
    ):
        self._champion = None
        self.mult = mult
        self._lane = None
        self._kills = 0
        self._deaths = 0
        self._assists = 0
        self._points = 0
        self.champions = champions
        super().__init__(
            player_id, nationality, first_name, last_name, birthday, nick_name, skill
        )

    @property
    def champion(self) -> Champion:
        return self._champion

    @property
    def lane(self) -> Lanes:
        return self._lane

    @property
    def kills(self) -> int:
        return self._kills

    @property
    def deaths(self) -> int:
        return self._deaths

    @property
    def assists(self) -> int:
        return self._assists

    @property
    def points(self) -> int:
        return self._points

    @champion.setter
    def champion(self, champion: Champion) -> None:
        self._champion = champion

    @lane.setter
    def lane(self, lane: int) -> None:
        for lane_name in Lanes:
            if lane == lane_name.value:
                self._lane = lane_name

    @kills.setter
    def kills(self, kills: int) -> None:
        self._kills = kills

    @deaths.setter
    def deaths(self, deaths: int) -> None:
        self._deaths = deaths

    @assists.setter
    def assists(self, assists: int) -> None:
        self._assists = assists

    @points.setter
    def points(self, add_pts: int) -> None:
        self._points = add_pts

    def reset_attributes(self) -> None:
        self.points = 0
        self.kills = 0
        self.deaths = 0
        self.assists = 0

    def get_highest_multiplier(self) -> float:
        """
        Gets the highest lane multiplier.
        """
        return max(self.mult)

    def get_best_lane(self) -> int:
        """
        Gets the highest lane multiplier, the lane that the player is 100% confident on playing.
        """
        return self.mult.index(self.get_highest_multiplier())

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
            return self.mult[self.lane.value]
        else:
            raise LaneError("Player may not be playing the game!")

    def get_curr_player_skill(self) -> float:
        """
        Gets the player's skill according to the lane he is currently at.
        """
        return self.skill * self.get_curr_lane_multiplier()

    def get_champion_skill(self) -> float:
        """
        Gets the player_champion_skill according to the multiplier.
        If for some reason a champion is not on the list, it receives a default multiplier of 0.5.
        """
        mult = 0.5  # default champion multiplier
        for champion in self.champions:
            if champion["id"] == self.champion.champion_id:
                mult = champion["mult"]
                break
        return (0.5 * self.champion.skill) + (0.5 * self.champion.skill * mult)

    def get_player_total_skill(self) -> float:
        """
        Gets the player + player_champion_skill + points to use in the match.
        This will define how strong or how weak a certain player is on the current match.
        """
        return (
            self.get_curr_player_skill() + self.get_champion_skill()
        ) / 2 + self.points

    def __repr__(self):
        return "{0} {1}".format(self.__class__.__name__, self.nick_name)

    def __str__(self):
        return "{0}".format(self.nick_name)