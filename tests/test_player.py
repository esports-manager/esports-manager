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

import unittest
import json
from tempfile import NamedTemporaryFile
import random

from src.core.player import Player
from src.core.match_live import load_list_from_json
from src.core.pre_match import create_player_object
from src.resources.generator.get_names import gen_nick_name, get_nick_team_names
from src.resources.generator.generate_players import generate_player_list
from src.resources.utils import write_to_json


def get_player_dict_test() -> dict:
    return {
        "first_name": "John",
        "last_name": "Doe",
        "nick_name": "Mock",
        "nationality": "Brazil",
        "id": 100,
        "skill": 80
    }


class PlayerTest(unittest.TestCase):
    def test_player_creation(self) -> None:
        player_dict = get_player_dict_test()
        player = create_player_object(player_dict)
        self.assertIsNotNone(player)


class MobaPlayerTest(unittest.TestCase):
    def setUp(self) -> None:
        player_dict = get_player_dict_test()
        self.player = create_player_object(player_dict)
        self.nick_names = get_nick_team_names('nicknames.txt')

    def test_player_creation(self) -> None:
        self.assertIsNotNone(self.player)

    def test_random_player_creation(self) -> None:
        player_list = load_list_from_json('players.json')
        player_dict = random.choice(player_list)
        player = create_player_object(player_dict)
        self.assertIsInstance(player, Player)

    def test_add_points(self) -> None:
        self.player.points = 5
        self.player.points += 3
        self.assertEqual(self.player.points, 8)

    def test_get_invalid_nicknames(self):
        with self.assertRaises(FileNotFoundError):
            get_nick_team_names('nick_names.txt')

    def test_generate_valid_nickname(self):
        nickname = gen_nick_name(self.nick_names)
        self.assertIsNotNone(nickname)
        self.assertIsNot(nickname, " ")

    def test_generate_player_list(self):
        players = generate_player_list()
        self.assertIsNotNone(players)
        self.assertGreater(len(players), 0)

    def test_generate_player_file(self):
        players = generate_player_list()
        with NamedTemporaryFile(mode='w') as temp_file:
            write_to_json(players, temp_file.name)
            with open(temp_file.name, 'r') as fp:
                contents = json.load(fp)

        self.assertIsNotNone(contents)
        self.assertEqual(players, contents)
        
        
if __name__ == '__main__':
    unittest.main()
