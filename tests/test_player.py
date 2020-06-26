import unittest
import json
from tempfile import NamedTemporaryFile
import random

from src.core.player import Player
from src.core.match_live import get_dict_list, create_player_object
from src.resources.generator.get_names import gen_nick_or_team_name
from src.resources.generator.generate_players import generate_player_list, generate_file


def get_player_dict_test() -> dict:
    return {
        "first_name": "John",
        "last_name": "Doe",
        "nick_name": "Mock",
        "nationality": "br",
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

    def test_player_creation(self) -> None:
        self.assertIsNotNone(self.player)

    def test_random_player_creation(self) -> None:
        player_list = get_dict_list('../src/resources/db/players.json')
        player_dict = random.choice(player_list)
        player = create_player_object(player_dict)
        self.assertIsInstance(player, Player)

    def test_add_points(self) -> None:
        self.player.points = 5
        self.player.points = 3
        self.assertEqual(self.player.points, 8)

    def test_generate_invalid_nickname(self):
        with self.assertRaises(FileNotFoundError):
            gen_nick_or_team_name("nick_names.txt")

    def test_generate_valid_nickname(self):
        nickname = gen_nick_or_team_name("nicknames.txt")
        self.assertIsNotNone(nickname)
        self.assertIsNot(nickname, " ")

    def test_generate_player_list(self):
        players = generate_player_list()
        self.assertIsNotNone(players)
        self.assertGreater(len(players), 0)

    def test_generate_player_file(self):
        players = generate_player_list()
        with NamedTemporaryFile(delete=False) as temp_file:
            generate_file(players, temp_file.name)
            with open(temp_file.name, 'r') as fp:
                contents = json.load(fp)
        self.assertIsNotNone(contents)
        self.assertEqual(players, contents)
        
        
if __name__ == '__main__':
    unittest.main()
