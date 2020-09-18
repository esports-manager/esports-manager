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

from src.core.pre_match import get_team, get_teams_dictionaries


class PreMatch(unittest.TestCase):
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
