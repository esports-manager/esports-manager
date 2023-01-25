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
import pytest

from core.esports.moba.generator import MobaPlayerGenerator


@pytest.fixture
def player_generator():
    return MobaPlayerGenerator()


def test_get_nationality(player_generator):
    pass


def test_generate_dob(player_generator):
    pass


def test_generate_champions(player_generator):
    pass


def test_generate_skill(player_generator):
    pass


def test_generate_name(player_generator):
    pass


def test_generate_nick(player_generator):
    pass


def test_get_dictionary(player_generator):
    pass


def test_get_object(player_generator):
    pass


def test_generate_multipliers(player_generator):
    pass


def test_generate_player(player_generator):
    pass


def test_generate_players(player_generator):
    pass


def test_get_players_dict(player_generator):
    pass


def test_get_players_objects(player_generator):
    pass


def test_generate_file(player_generator):
    pass
