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
