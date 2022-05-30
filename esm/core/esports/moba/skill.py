#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2022  Pedrenrique G. Guimarães
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
from enum import Enum, auto
from typing import Union


class SkillError(Exception):
    pass


class SkillGain(Enum):
    FAST = auto()
    MEDIUM = auto()
    SLOW = auto()


class Skill:
    def __init__(self, skill: int, exp: float = 0.0, skill_gain: Union[SkillGain, str] = SkillGain.MEDIUM):
        self.skill = skill
        self.skill_gain = None
        self.get_skill_gain_value(skill_gain)
        self.current_skill = skill
        self.exp = exp
        self.total_exp = self.get_total_exp()
        self._exp_to_next_level = self.exp_to_next_level()

    def is_max_lvl(self) -> bool:
        return self.skill == 99

    def get_skill_gain_value(self, skill_gain: Union[SkillGain, str]):
        if isinstance(skill_gain, SkillGain):
            self.skill_gain = skill_gain
        elif isinstance(skill_gain, str):
            sk_g = list(SkillGain)
            for i in sk_g:
                if i.name == skill_gain:
                    self.skill_gain = i
                    break
        else:
            raise SkillError("Skill gain value is invalid!")

    def get_total_exp(self):
        if self.skill_gain == SkillGain.FAST:
            total_exp = (133.33 * self.skill**3) + (24.909 * self.skill**2) + (7.3154 * self.skill) + 174.16
        elif self.skill_gain == SkillGain.MEDIUM:
            total_exp = (100.0 * self.skill**3) + (60.0 * self.skill**2) + self.skill + 161.0
        else:
            total_exp = (66.667 * self.skill**3) + (9.9819 * self.skill**2) + (85.254 * self.skill) + 94.64

        return total_exp + self.exp

    def exp_to_next_level(self):
        if self.skill <= 0:
            raise SkillError("Skill level must not be zero or negative!")

        if self.is_max_lvl():
            self._exp_to_next_level = 0
        elif self.skill_gain == SkillGain.FAST:
            self._exp_to_next_level = (200.0 * self.skill**2) + (220.0 * self.skill) + 161.0
        elif self.skill_gain == SkillGain.MEDIUM:
            self._exp_to_next_level = (300.0 * self.skill**2) + (420.0 * self.skill) + 161.0
        else:
            self._exp_to_next_level = (400.0 * self.skill ** 2) + (450.0 * self.skill) + 161.0

        self._exp_to_next_level -= self.exp

        return self._exp_to_next_level

    def calculate_current_skill(self, mult: float):
        self.current_skill = self.skill * mult

    def add_exp_points(self, exp_points: float):
        """
        Adds exp points after each match.

        If the exp reaches a limit to the skill lvl, increases the skill points.

        Players get more exp points if they beat a harder team.
        """
        points = exp_points

        while points >= self.exp_to_next_level() and not self.is_max_lvl():
            exp_to_next_lvl = self.exp_to_next_level()
            points -= exp_to_next_lvl
            self.skill += 1

        self.exp = points
        self.total_exp += exp_points

        if self.is_max_lvl():
            self.exp = 0
            self.total_exp = self.get_total_exp()

    def __str__(self):
        return self.skill
