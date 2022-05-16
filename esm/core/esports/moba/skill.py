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

class SkillError(Exception):
    pass


class Skill:
    def __init__(self, skill: int, exp: float = 0.0):
        self.skill = skill
        self.current_skill = skill
        self.exp = exp
        self._exp_to_next_level = self.exp_to_next_level

    @property
    def exp_to_next_level(self):
        if self.skill <= 0:
            raise SkillError("Skill level must not be zero or negative!")
        # Testing this formula
        # self._exp_to_next_level = (3 * self.skill**2) + (2.9964 * self.skill) + 1.0909
        self._exp_to_next_level = (300 * self.skill**2) + (420 * self.skill) + 161
        return self._exp_to_next_level

    def calculate_current_skill(self, mult: float):
        self.current_skill = self.skill * mult

    def add_exp_points(self, exp_points: float):
        """
        Adds exp points after each match.

        If the exp reaches a limit to the skill lvl, increases the skill points.

        Players get more exp points if they beat a harder team.
        """
        self.exp += exp_points

        # Max skill level
        if self.skill != 99:
            diff_exp = self.exp_to_next_level - self.exp
            if diff_exp <= 0:
                self.skill += 1
                self.exp = abs(diff_exp)

    def __str__(self):
        return self.skill
