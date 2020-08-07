import unittest

from src.core.match_live import get_live_obj_test


class MatchLiveTest(unittest.TestCase):
    def setUp(self) -> None:
        self.live = get_live_obj_test()
        self.match = self.live.match

    def test_get_team_win_prob(self) -> None:
        self.live.calculate_both_teams_win_prob()
        prob = self.match.team1.win_prob + self.match.team2.win_prob
        self.assertEqual(1, prob)


if __name__ == '__main__':
    unittest.main()
