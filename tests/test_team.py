import unittest

from src.core.team import Team
from src.core.match_live import get_match_obj_test, get_team, get_dict_list


class TeamTest(unittest.TestCase):
    def setUp(self) -> None:
        match = get_match_obj_test()
        self.team = match.team1

    def test_player_skill(self):
        self.assertGreaterEqual(self.team.player_overall, 0)

    def test_champion_overall(self):
        self.assertGreaterEqual(self.team.champion_overall, 0)

    def test_get_team(self):
        teams = get_dict_list("../src/resources/db/teams.json")
        team = get_team(-1, teams)
        self.assertRaises(ValueError)


if __name__ == '__main__':
    unittest.main()
