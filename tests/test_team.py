import unittest
from tempfile import NamedTemporaryFile

from src.core.match_live import get_live_obj_test
from src.core.pre_match import get_team
from src.resources.generator.generate_teams import *
from src.resources.generator.get_names import gen_team_name, get_nick_team_names


class TeamTest(unittest.TestCase):
    def setUp(self) -> None:
        live = get_live_obj_test()
        match = live.match
        self.team_names = get_nick_team_names('team_names.txt')
        self.team = match.team1

    def test_player_skill(self):
        self.assertGreaterEqual(self.team.player_overall, 0)

    def test_champion_overall(self):
        self.assertGreaterEqual(self.team.champion_overall, 0)

    def test_get_invalid_team(self):
        teams = load_list_from_json('teams.json')
        with self.assertRaises(ValueError):
            get_team(-1, teams)

    def test_get_valid_team(self):
        teams = load_list_from_json('teams.json')
        team = get_team(0, teams)
        self.assertIsNotNone(team)
        self.assertEqual(team, teams[0])

    def test_get_players(self):
        players = load_list_from_json('players.json')
        self.assertIsNotNone(players)

    def test_invalid_get_team_name(self):
        with self.assertRaises(FileNotFoundError):
            get_nick_team_names('teamname.txt')

    def test_generate_team_name(self):
        name = gen_team_name(self.team_names)
        self.assertIsNotNone(name)
        self.assertIsNot(" ", name)

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
            write_to_json(contents, temp_file.name)
            with open(temp_file.name, 'r') as f:
                obtained_content = json.load(f)
        self.assertIsNotNone(obtained_content)
        self.assertEqual(contents, obtained_content)

    def test_is_tower_up(self):
        self.assertEqual(True, self.team.is_tower_up('mid'))

    def test_is_tower_not_up(self):
        self.team.towers["mid"] = 0
        self.assertEqual(False, self.team.is_tower_up('mid'))

    def test_are_all_towers_up(self):
        self.assertEqual(True, self.team.are_all_towers_up())

    def test_are_all_towers_not_up(self):
        for key, _ in self.team.towers.items():
            self.team.towers[key] = 0

        self.assertEqual(False, self.team.are_all_towers_up())

    def test_one_tower_is_not_up(self):
        self.team.towers['mid'] = 0
        self.assertEqual(False, self.team.are_all_towers_up())

    def test_get_points(self):
        for player in self.team.list_players:
            player.points += 5

        self.assertEqual(25, self.team.points)


if __name__ == '__main__':
    unittest.main(verbosity=2)
