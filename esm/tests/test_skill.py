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
import pytest
from esm.core.esports.moba.skill import Skill, SkillError


def test_lvl_up_once():
    skill = Skill(50, exp=0.0)
    exp_necessary = skill.exp_to_next_level()
    skill.add_exp_points(exp_necessary)
    assert exp_necessary > 0
    assert skill.skill == 51


def test_lvl1_exp_necessary():
    skill = Skill(1, exp=0.0)
    exp_necessary = skill.exp_to_next_level()
    skill.add_exp_points(exp_necessary)
    assert exp_necessary > 0
    assert skill.skill == 2


def test_preexisting_exp_lvl_up():
    skill = Skill(50, exp=0.0)
    skill2 = Skill(50, exp=500.0)
    exp_necessary = skill.exp_to_next_level()
    exp_necessary2 = skill2.exp_to_next_level()
    diff_exp = exp_necessary - exp_necessary2
    assert diff_exp == 500.0


def test_lvlup_more_than_once():
    skill = Skill(50, exp=0.0)
    skill2 = Skill(51, exp=0.0)
    exp_necessary = skill.exp_to_next_level()
    exp_necessary += skill2.exp_to_next_level()
    skill.add_exp_points(exp_necessary)
    assert skill.skill == 52


def test_max_lvl_up():
    skill = Skill(99, exp=0.0)
    exp_necessary = skill.exp_to_next_level()
    skill.add_exp_points(exp_necessary)
    assert exp_necessary == 0
    assert skill.skill == 99


def test_lvlup_till_max():
    skill = Skill(97)
    skill2 = Skill(98)
    exp_necessary = skill.exp_to_next_level()
    exp_necessary += skill2.exp_to_next_level()
    skill.add_exp_points(exp_necessary)
    assert skill.skill == 99


def test_negative_skill_level():
    with pytest.raises(SkillError):
        Skill(-1)


def test_zero_skill_level():
    with pytest.raises(SkillError):
        Skill(0)
