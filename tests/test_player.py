import unittest
import random

from src.core.player import Player
from src.core.match_live import get_dict_list, create_player_object


def get_player_dict_test() -> dict:
    player_dict = {
        "first_name": "John",
        "last_name": "Doe",
        "nick_name": "Mock",
        "nationality": "br",
        "id": 100,
        "skill": 80
    }

    return player_dict


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


if __name__ == '__main__':
    unittest.main()
