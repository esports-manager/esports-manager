import unittest

from src.core.pre_match import get_team


class MyTestCase(unittest.TestCase):
    def test_get_team(self):
        expected_team = {
            "id": 1,
            "name": "TestTeam",
        }
        team_list = [expected_team, {"id": 2, "name": "TestTeam2"}]
        team = get_team(1, team_list)
        self.assertEqual(team, expected_team)


if __name__ == '__main__':
    unittest.main()
