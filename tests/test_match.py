import unittest

from src.core.match_live import get_match_obj_test
from src.core.match import Match


class MatchTest(unittest.TestCase):
    def setUp(self) -> None:
        self.match = get_match_obj_test()

    def test_get_match(self) -> None:
        self.assertIsNotNone(self.match)
        self.assertIsInstance(self.match, Match)

    def test_get_team_win_prob(self) -> None:
        self.match.calculate_both_teams_win_prob()
        prob = self.match.team1.win_prob + self.match.team2.win_prob
        self.assertEqual(1, prob)

    @unittest.expectedFailure
    def test_total_prob(self):
        total_prob = sum(
            team.player_overall + team.champion_overall for team in self.match.teams
        )

        self.assertEqual(0, total_prob)

    @unittest.expectedFailure
    def test_team1_sum(self):
        self.assertEqual(0, self.match.team1.champion_overall + self.match.team2.player_overall)

    @unittest.expectedFailure
    def test_team2_sum(self):
        self.assertEqual(0, self.match.team2.player_overall + self.match.team2.champion_overall)


if __name__ == '__main__':
    unittest.main()
