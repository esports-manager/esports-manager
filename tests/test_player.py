import unittest
import random

from src.core.player import Player
from src.core.match_live import get_dict_list, create_player_object


class MyTestCase(unittest.TestCase):
    def test_add_points(self):
        player_dict = get_dict_list('../resources/db/players.json')
        pl_id_dict = random.choice(player_dict)
        player = create_player_object(pl_id_dict)
        player.points = 2
        player.points = 3
        self.assertEqual(player.points, 5)


if __name__ == '__main__':
    unittest.main()
