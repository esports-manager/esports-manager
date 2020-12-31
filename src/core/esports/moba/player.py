#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020  Pedrenrique G. Guimarães
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

from src.core.esports.moba.moba_enums_def import Lanes, LaneError
from src.core.esports.moba.champion import Champion


class Player:
    def __init__(self,
                 player_id: int,
                 nationality: str,
                 first_name: str,
                 last_name: str,
                 birthday: date,
                 nick_name: str,
                 skill: int):
        self.player_id = player_id

        # TODO: players should include team's id as well

        self.first_name = first_name
        self.last_name = last_name
        self.birthday = birthday

        self.nick_name = nick_name

        self.nationality = nationality

        # TODO: replace skill by attribute dictionary
        self._skill = skill

        # TODO: players should have a "potential" value too. This value tells the game that the player
        # can improve his overall skill to a certain level

    @property
    def skill(self) -> int:
        return self._skill

    @skill.setter
    def skill(self, skill):
        self._skill = skill


class MobaPlayer(Player):
    def __init__(self,
                 player_id: int,
                 nationality: str,
                 first_name: str,
                 last_name: str,
                 birthday: date,
                 nick_name: str,
                 mult: list,
                 skill: int,
                 champions: list):
        self._champion = None
        self.mult = mult
        self._lane = None
        self._kills = 0
        self._deaths = 0
        self._assists = 0
        self._points = 0
        self.champions = champions
        super().__init__(player_id, nationality, first_name, last_name, birthday, nick_name, skill)

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
    def champion(self, champion: Champion):
        self._champion = champion

    @lane.setter
    def lane(self, lane: int):
        for lane_name in Lanes:
            if lane == lane_name.value:
                self._lane = lane_name

    @kills.setter
    def kills(self, kills: int):
        self._kills = kills

    @deaths.setter
    def deaths(self, deaths: int):
        self._deaths = deaths

    @assists.setter
    def assists(self, assists: int):
        self._assists = assists

    @points.setter
    def points(self, add_pts: int):
        self._points = add_pts

    def get_highest_multiplier(self) -> float:
        return max(self.mult)

    def get_best_lane(self) -> int:
        return self.mult.index(self.get_highest_multiplier())

    def get_default_lane(self):
        lane = self.get_best_lane()
        self.lane = lane
    
    def get_curr_lane_multiplier(self):
        if self.lane is not None:
            return self.mult[self.lane.value]
        else:
            raise LaneError('Player may not be playing the game!')

    def get_age(self, today: date) -> int:
        age = today - self.birthday
        return int(age.days * 0.0027379070)

    def get_curr_player_skill(self):
        return self.skill * self.get_curr_lane_multiplier()

    def get_champion_skill(self):
        mult = 0.5  # default champion multiplier
        for champion in self.champions:
            if champion['id'] == self.champion.champion_id:
                mult = champion['mult']
                break
        return self.champion.skill * mult

    def get_player_total_skill(self):
        return self.get_curr_player_skill() + self.get_champion_skill() + self.points

    def __repr__(self):
        return '{0} {1}'.format(self.__class__.__name__, self.nick_name)

    def __str__(self):
        return '{0}'.format(self.nick_name)
