import unittest
import random

from src.core.player import Player, MobaPlayer
from src.core.match_live import get_dict_list, create_player_object


def get_player_dict_test() -> dict:
    player_dict = {
        "first_name": "John",
        "last_name": "Doe",
        "nick_name": "Mock",
        "id": 100,
        "skill": 80
    }

    return player_dict


class PlayerTest(unittest.TestCase):
    def test_player_creation(self) -> Player:
        player_dict = get_player_dict_test()
        player = create_player_object(player_dict)
        self.assertIsNotNone(player)


class MobaPlayerTest(unittest.TestCase):
    def test_player_creation(self) -> MobaPlayer:
        player_dict = get_player_dict_test()
        player = create_player_object(player_dict)
        self.assertIsNotNone(player)

    def test_random_player_creation(self):
        player_list = get_dict_list('../src/resources/db/players.json')
        player_dict = random.choice(player_list)
        player = create_player_object(player_dict)
        self.assertIsInstance(player, Player)


if __name__ == '__main__':
    unittest.main()
