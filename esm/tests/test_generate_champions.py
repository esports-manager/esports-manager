#      eSports Manager - free and open source eSports Management game
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

from esm.core.esports.moba.champion import ChampionDifficulty, ChampionType, Lanes
from esm.core.esports.moba.generator.default_champion_defs import (
    get_default_champion_defs,
)
from esm.core.esports.moba.generator.generate_champions import (
    ChampionGenerator,
    ChampionGeneratorError,
)


@pytest.fixture
def champion_gen() -> ChampionGenerator:
    return ChampionGenerator()


def test_generate_champion(champion_gen: ChampionGenerator):
    champion = champion_gen.generate(champion_def=None)
    assert champion is not None


def test_generate_champion_from_dict(champion_gen: ChampionGenerator):
    champion_dict = {
        "name": "MyChampion",
        "lanes": [Lanes.TOP.name, Lanes.JNG.name],
        "champion_difficulty": ChampionDifficulty.MEDIUM.value,
        "champion_type1": ChampionType.TANK.value,
        "champion_type2": ChampionType.FIGHTER.value,
    }
    obtained_champion = champion_gen.generate(champion_dict)
    assert obtained_champion.name == champion_dict["name"]
    assert obtained_champion.lanes.top == 1.0
    assert obtained_champion.lanes.jng == 1.0
    assert obtained_champion.champion_difficulty == ChampionDifficulty.MEDIUM
    assert obtained_champion.champion_type1 == ChampionType.TANK
    assert obtained_champion.champion_type2 == ChampionType.FIGHTER


def test_generate_champion_from_dict_without_champion_type(
    champion_gen: ChampionGenerator,
):
    champion_dict = {
        "name": "MyChampion",
        "lanes": [Lanes.SUP.name, Lanes.JNG.name],
        "champion_difficulty": ChampionDifficulty.MEDIUM.value,
    }
    obtained_champion = champion_gen.generate(champion_dict)
    assert obtained_champion.champion_type1 is not None


def test_generate_champion_from_dict_with_none_champion_type(
    champion_gen: ChampionGenerator,
):
    champion_dict = {
        "name": "MyChampion",
        "lanes": [Lanes.MID.name, Lanes.ADC.name],
        "champion_difficulty": ChampionDifficulty.MEDIUM.value,
        "champion_type1": ChampionType.TANK.value,
        "champion_type2": None,
    }
    obtained_champion = champion_gen.generate(champion_dict)
    assert obtained_champion.champion_type1 == ChampionType.TANK
    assert obtained_champion.champion_type2 is None


def test_raises_error_if_champion_type1_is_none(champion_gen: ChampionGenerator):
    with pytest.raises(ChampionGeneratorError):
        champion_dict = {
            "name": "MyChampion",
            "lanes": [Lanes.TOP.name, Lanes.ADC.name],
            "champion_difficulty": ChampionDifficulty.MEDIUM.value,
            "champion_type1": None,
            "champion_type2": ChampionType.TANK.value,
        }
        champion_gen.generate(champion_dict)


def test_generate_many_champions(champion_gen: ChampionGenerator):
    champ_defs = get_default_champion_defs()
    for champ_def in champ_defs:
        obtained_champion = champion_gen.generate(champ_def)
        assert obtained_champion.name == champ_def["name"]
        for lane in champ_def["lanes"]:
            if lane == "TOP":
                assert obtained_champion.lanes.top == 1.0
            elif lane == "JNG":
                assert obtained_champion.lanes.jng == 1.0
            elif lane == "MID":
                assert obtained_champion.lanes.mid == 1.0
            elif lane == "ADC":
                assert obtained_champion.lanes.adc == 1.0
            elif lane == "SUP":
                assert obtained_champion.lanes.sup == 1.0
        assert obtained_champion.champion_difficulty is not None
        assert obtained_champion.champion_type1 is not None
        assert obtained_champion.champion_type2 != obtained_champion.champion_type1
