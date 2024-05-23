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
import hypothesis.strategies as st
import pytest
from hypothesis import given

from esm.core.esports.moba.champion import (
    Champion,
    ChampionDifficulty,
    ChampionLoadError,
    ChampionType,
)
from esm.core.esports.moba.moba_definitions import (
    LaneMultiplierError,
    LaneMultipliers,
    Lanes,
)


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
        champion.skill * champion.lanes.sup,
    ]
    champion_lanes = [champion.get_current_skill(lane) for lane in Lanes]
    assert expected_output == champion_lanes


def test_get_best_lane(champion: Champion):
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


@given(
    st.builds(
        Champion,
        champion_id=st.uuids(),
        name=st.text(),
        skill=st.integers(),
        scaling_factor=st.floats(min_value=0.1, max_value=1.0),
        scaling_peak=st.integers(min_value=1, max_value=30),
        lanes=st.builds(
            LaneMultipliers,
            top=st.floats(min_value=0.1, max_value=1.0),
            jng=st.floats(min_value=0.1, max_value=1.0),
            mid=st.floats(min_value=0.1, max_value=1.0),
            adc=st.floats(min_value=0.1, max_value=1.0),
            sup=st.floats(min_value=0.1, max_value=1.0),
        ),
        champion_difficulty=st.sampled_from(ChampionDifficulty),
        champion_type1=st.sampled_from(ChampionType),
        champion_type2=st.sampled_from(ChampionType),
    )
)
def test_generated_champion(champion: Champion):
    assert isinstance(champion, Champion)
    assert champion.champion_type2 != champion.champion_type1
    assert champion.champion_difficulty is not None
    assert champion.lanes is not None
