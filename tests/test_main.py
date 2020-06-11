import unittest

from src.core.match_live import get_match_obj


class MyTestCase(unittest.TestCase):
    def test_get_match(self):
        match = get_match_obj()

        self.assertIsNotNone(match)

    def test_get_pl_skill(self):
        match = get_match_obj()

        team1_pl_skill = match.team1.player_overall
        team2_pl_skill = match.team2.player_overall

        self.assertIsNotNone(team1_pl_skill)
        self.assertIsNotNone(team2_pl_skill)

    def test_get_ch_skill(self):
        match = get_match_obj()

        team1_ch_skill = match.team1.champion_overall
        team2_ch_skill = match.team2.champion_overall

        self.assertIsNotNone(team1_ch_skill)
        self.assertIsNotNone(team2_ch_skill)
        self.assertLessEqual(0, team1_ch_skill)
        self.assertLessEqual(0, team2_ch_skill)


if __name__ == '__main__':
    unittest.main()
