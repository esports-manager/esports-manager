import unittest
import json
from tempfile import NamedTemporaryFile

from src.core.match_live import get_match_obj_test, get_team, get_dict_list
from src.resources.generator.generate_teams import *
from src.resources.generator.get_names import gen_nick_or_team_name
from src.resources.generator.generate_players import generate_file


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

    def test_generate_team_file(self):
        players = [
            {"id": 1},
            {"id": 2},
            {"id": 3},
            {"id": 4},
            {"id": 5}
        ]
        contents = generate_teams(players)
        with NamedTemporaryFile(delete=False) as temp_file:
            generate_file(contents, temp_file.name)
            with open(temp_file.name, 'r') as f:
                obtained_content = json.load(f)
        self.assertIsNotNone(obtained_content)
        self.assertEqual(contents, obtained_content)


if __name__ == '__main__':
    unittest.main(verbosity=2)
