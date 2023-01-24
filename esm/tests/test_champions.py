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
import uuid

from esm.core.esports.moba.champion import Champion
from esm.core.esports.moba.moba_enums_def import Lanes


def test_serialize_champion():
    expected_champion = {
        "id": '00000000000000000000000000000001',
        "name": "Champion",
        "lanes": {
            0: 1.0,
            1: 1.0,
            2: 0.45,
            3: 0.3,
            4: 0.0,
        },
        "skill": 87
    }
    lanes = {
        Lanes.TOP: 1.0,
        Lanes.JNG: 1.0,
        Lanes.MID: 0.45,
        Lanes.ADC: 0.3,
        Lanes.SUP: 0.0,
    }
    champion = Champion(uuid.UUID(int=1), "Champion", 87, lanes)
    assert expected_champion == champion.serialize()


def test_get_from_dict():
    lanes = {
        Lanes.TOP: 1.0,
        Lanes.JNG: 1.0,
        Lanes.MID: 0.45,
        Lanes.ADC: 0.3,
        Lanes.SUP: 0.0,
    }
    expected_champion = Champion(uuid.UUID(int=1), "Champion", 87, lanes)
    champion_dict = {
        "id": '00000000000000000000000000000001',
        "name": "Champion",
        "lanes": {
            0: 1.0,
            1: 1.0,
            2: 0.45,
            3: 0.3,
            4: 0.0,
        },
        "skill": 87
    }
    assert Champion.get_from_dict(champion_dict) == expected_champion


def test_champion_name_str():
    lanes = {
        Lanes.TOP: 1.0,
        Lanes.JNG: 1.0,
        Lanes.MID: 0.45,
        Lanes.ADC: 0.3,
        Lanes.SUP: 0.0,
    }
    champion = Champion(uuid.UUID(int=1), "MyChampion", 87, lanes)
    assert "MyChampion" == champion.__str__()
