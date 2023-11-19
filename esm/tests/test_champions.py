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

from esm.core.esports.moba.champion import Champion, ChampionLoadError
from esm.core.esports.moba.moba_definitions import Lanes, LaneMultiplierError


def test_serialize_champion(champion: Champion, champion_dict: dict):
    assert champion_dict == champion.serialize()


def test_get_from_dict(champion: Champion, champion_dict: dict):
    assert Champion.get_from_dict(champion_dict) == champion


def test_champion_name_str(champion: Champion):
    assert "MyChampion" == champion.__str__()


def test_get_current_skill(champion: Champion):
    expected_output = [
        champion.skill * champion.lanes.top,
        champion.skill * champion.lanes.jng,
        champion.skill * champion.lanes.mid,
        champion.skill * champion.lanes.adc,
        champion.skill * champion.lanes.sup
    ]
    champion_lanes = [champion.get_current_skill(lane) for lane in Lanes]
    assert expected_output == champion_lanes


def test_get_best_lane(champion):
    expected_lane = Lanes.JNG
    assert expected_lane == champion.lanes.get_best_attribute()


def test_get_champion_with_negative_skill(champion_dict):
    champion_dict["skill"] = -100
    with pytest.raises(ChampionLoadError):
        Champion.get_from_dict(champion_dict)


def test_get_champion_with_more_than_max_skill(champion_dict):
    champion_dict["skill"] = 101
    with pytest.raises(ChampionLoadError):
        Champion.get_from_dict(champion_dict)


def test_get_champion_with_negative_multipliers(champion_dict):
    champion_dict["lanes"] = {
        Lanes.TOP.value: -1.00,
        Lanes.JNG.value: 1.00,
        Lanes.MID.value: 0.45,
        Lanes.ADC.value: 0.30,
        Lanes.SUP.value: 0.10,
    }
    with pytest.raises(LaneMultiplierError):
        Champion.get_from_dict(champion_dict)


def test_get_champion_with_more_than_max_multiplier(champion_dict):
    champion_dict["lanes"] = {
        Lanes.TOP.value: 1.00,
        Lanes.JNG.value: 1.00,
        Lanes.MID.value: 0.45,
        Lanes.ADC.value: 0.30,
        Lanes.SUP.value: 1.10,
    }
    with pytest.raises(LaneMultiplierError):
        Champion.get_from_dict(champion_dict)
