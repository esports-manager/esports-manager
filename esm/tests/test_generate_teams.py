#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2024  Pedrenrique G. Guimarães
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
# import uuid
#
# import pytest
#
# from ..core.esports.moba.champion import (
#     Champion,
#     ChampionDifficulty,
#     ChampionType,
#     LaneMultipliers,
# )
# from ..core.esports.moba.generator.generate_teams import (
#     TeamGenerator,
#     TeamGeneratorError,
# )
# from ..core.esports.moba.team import Team
#
#
# def mock_team_definition() -> dict[str, int | str]:
#     return {
#         "name": "TeamTest",
#         "nationality": "Korea",
#         "mu": 80,
#         "sigma": 10,
#     }
#
#
# @pytest.fixture
# def team_generator() -> TeamGenerator:
#
#     return TeamGenerator()
#
#
# def test_team_generator_champion_list_is_empty():
#     with pytest.raises(TeamGeneratorError):
#         TeamGenerator(champions=[], player_names=[])
#
#
# def test_generate_team(team_generator):
#     teams = team_generator.generate()
#     assert isinstance(teams, Team)
