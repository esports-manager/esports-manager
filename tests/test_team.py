import unittest

from src.core.team import Team
from src.core.match_live import get_match_obj_test, get_team, get_dict_list
from src.resources.generator.generate_teams import *
from src.resources.generator.get_names import gen_nick_or_team_name


class TeamTest(unittest.TestCase):
    def setUp(self) -> None:
        match = get_match_obj_test()
        self.team = match.team1

    def test_player_skill(self):
        self.assertGreaterEqual(self.team.player_overall, 0)

    def test_champion_overall(self):
        self.assertGreaterEqual(self.team.champion_overall, 0)

    def test_get_invalid_team(self):
        teams = get_dict_list("../src/resources/db/teams.json")
        with self.assertRaises(ValueError):
            get_team(-1, teams)

    def test_get_valid_team(self):
        teams = get_dict_list("../src/resources/db/teams.json")
        team = get_team(0, teams)
        self.assertIsNotNone(team)
        self.assertEqual(team, teams[0])

    def test_get_players(self):
        players = get_players()
        self.assertIsNotNone(players)

    def test_invalid_generate_team_name(self):
        with self.assertRaises(FileNotFoundError):
            gen_nick_or_team_name("teamname.txt")

    def test_generate_team_name(self):
        name = gen_nick_or_team_name("team_names.txt")
        self.assertIsNotNone(name)
        self.assertIsNot(name, " ")


if __name__ == '__main__':
    unittest.main()
