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
import uuid

import pytest

from esm.core.utils import load_list_from_file

from ..core.esports.moba.champion import Champion
from ..core.esports.moba.generator.generate_teams import (
    TeamGenerator,
    TeamGeneratorError,
)
from ..core.esports.moba.mobateam import MobaTeam
from ..core.esports.moba.player import MobaPlayer


def mock_team_definition() -> dict[str, int | str]:
    return {
        "name": "TeamTest",
        "nationality": "Korea",
        "mu": 80,
        "sigma": 10,
    }


def mock_team_definitions() -> list[dict[str, int | str]]:
    return [
        {
            "name": "KoreanTeam",
            "nationality": "Korea",
            "mu": 88,
            "sigma": 15,
        },
        {
            "name": "GermanTeam",
            "nationality": "Germany",
            "mu": 75,
            "sigma": 20,
        },
        {
            "name": "ChineseTeam",
            "nationality": "China",
            "mu": 89,
            "sigma": 10,
        },
    ]


@pytest.fixture
def team_generator(
    mock_champions: list[Champion], names_file: list[dict[str, str | float]]
) -> TeamGenerator:
    return TeamGenerator(champions=mock_champions, player_names=names_file)


def test_team_generator_champion_list_is_empty():
    with pytest.raises(TeamGeneratorError):
        TeamGenerator(champions=[], player_names=[])


def test_generate_team(team_generator):
    team_def = mock_team_definition()
    team = team_generator.generate(team_definition=team_def)
    assert isinstance(team, MobaTeam)
    assert team.name == team_def["name"]
    assert team.nationality == team_def["nationality"]
    for player in team.roster:
        assert isinstance(player, MobaPlayer)


def test_generate_multiple_teams(team_generator):
    teams = [team_generator.generate(team_def) for team_def in mock_team_definitions()]
    for team, team_def in zip(teams, mock_team_definitions()):
        assert isinstance(team, MobaTeam)
        assert team.name == team_def["name"]
        assert team.nationality == team_def["nationality"]
        assert team.roster is not None
