#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020  Pedrenrique G. Guimarães
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

import unittest

from src.core.match_live import get_live_obj_test
from src.core.match import Match


class MatchTest(unittest.TestCase):
    def setUp(self) -> None:
        self.live = get_live_obj_test()
        self.match = self.live.match

    def test_get_match(self) -> None:
        self.assertIsNotNone(self.match)
        self.assertIsInstance(self.match, Match)

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
