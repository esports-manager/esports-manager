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
        self.max_exp = 200000

    @property
    def exp_to_next_level(self):
        if self.skill > 1:
            self._exp_to_next_level = (6/5 * self.skill**3) - (15 * self.skill**2) + (100 * self.skill) - 140
        elif self.skill == 1:
            self._exp_to_next_level = 9
        else:
            raise SkillError("Skill level must not be zero or negative!")
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

    def get_exp_points(self, team1_skill_lvl: int, team2_skill_lvl: int, boost: float = 1.0):
        # TODO: move this to another module
        exp = ((team1_skill_lvl/5) * ((2 * team1_skill_lvl + 10) / (team1_skill_lvl + team2_skill_lvl + 10))**2.5) * (team1_skill_lvl + 150) * boost

        if exp > self.max_exp:
            exp = self.max_exp
        return exp

    def __str__(self):
        return self.skill
