#      Copyright (C) 2020-2023  Pedrenrique G. Guimarães
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
import pytest
import uuid

from esm.core.esports.moba.champion import Champion, ChampionLoadError
from esm.core.esports.moba.moba_enums_def import Lanes


@pytest.fixture
def champion():
    lanes = {
        Lanes.TOP: 1.0,
        Lanes.JNG: 1.0,
        Lanes.MID: 0.45,
        Lanes.ADC: 0.3,
        Lanes.SUP: 0.0,
    }
    return Champion(uuid.UUID(int=1), "MyChampion", 87, lanes)


@pytest.fixture
def champion_dict():
    return {
        "id": '00000000000000000000000000000001',
        "name": "MyChampion",
        "lanes": {
            0: 1.0,
            1: 1.0,
            2: 0.45,
            3: 0.3,
            4: 0.0,
        },
        "skill": 87
    }


def test_serialize_champion(champion: Champion, champion_dict: dict):
    assert champion_dict == champion.serialize()


def test_get_from_dict(champion: Champion, champion_dict: dict):
    assert Champion.get_from_dict(champion_dict) == champion


def test_champion_name_str(champion: Champion):
    assert "MyChampion" == champion.__str__()


def test_get_current_skill(champion: Champion):
    expected_output = [mult for _, mult in champion.lanes.items()]
    champion_lanes = [champion.get_current_skill(lane) for lane in Lanes]
    assert expected_output == champion_lanes


def test_get_champion_with_negative_skill():
    champion_dict = {
        "id": '00000000000000000000000000000001',
        "name": "MyChampion",
        "lanes": {
            0: 1.0,
            1: 1.0,
            2: 0.45,
            3: 0.3,
            4: 0.0,
        },
        "skill": -1
    }
    with pytest.raises(ChampionLoadError):
        Champion.get_from_dict(champion_dict)


def test_get_champion_with_more_than_max_skill():
    champion_dict = {
        "id": '00000000000000000000000000000001',
        "name": "MyChampion",
        "lanes": {
            0: 1.0,
            1: 1.0,
            2: 0.45,
            3: 0.3,
            4: 0.0,
        },
        "skill": 100
    }
    with pytest.raises(ChampionLoadError):
        Champion.get_from_dict(champion_dict)


def test_get_champion_with_negative_multipliers():
    champion_dict = {
        "id": '00000000000000000000000000000001',
        "name": "MyChampion",
        "lanes": {
            0: -1.0,
            1: 1.0,
            2: 0.45,
            3: 0.3,
            4: 0.0,
        },
        "skill": 87,
    }
    with pytest.raises(ChampionLoadError):
        Champion.get_from_dict(champion_dict)


def test_get_champion_with_big_multipliers():
    champion_dict = {
        "id": '00000000000000000000000000000001',
        "name": "MyChampion",
        "lanes": {
            0: 1.0,
            1: 1.0,
            2: 1.1,
            3: 0.3,
            4: 0.0,
        },
        "skill": 100
    }
    with pytest.raises(ChampionLoadError):
        Champion.get_from_dict(champion_dict)
