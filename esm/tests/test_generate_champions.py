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

from esm.core.esports.moba.generator.generate_champions import ChampionGenerator
from esm.core.esports.moba.champion import Champion, ChampionType, ChampionDifficulty


@pytest.fixture
def champion_gen() -> ChampionGenerator:
    return ChampionGenerator()


def test_generate_champion(champion_gen: ChampionGenerator):
    champion = champion_gen.generate(champion_def=None)
    assert champion is not None


def test_generate_champion_from_dict(champion_gen: ChampionGenerator):
    champion_dict = {
        "name": "MyChampion",
        "lanes": ["TOP", "JNG"],
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


def test_generate_champion_from_dict_without_champion_type(champion_gen: ChampionGenerator):
    champion_dict = {
        "name": "MyChampion",
        "lanes": ["SUP", "JNG"],
        "champion_difficulty": ChampionDifficulty.MEDIUM.value,
    }
    obtained_champion = champion_gen.generate(champion_dict)
    assert obtained_champion.champion_type1 is not None


def test_generate_champion_from_dict_with_none_champion_type(champion_gen: ChampionGenerator):
    champion_dict = {
        "name": "MyChampion",
        "lanes": ["MID", "ADC"],
        "champion_difficulty": ChampionDifficulty.MEDIUM.value,
        "champion_type1": ChampionType.TANK.value,
        "champion_type2": None,
    }
    obtained_champion = champion_gen.generate(champion_dict)
    assert obtained_champion.champion_type1 == ChampionType.TANK
    assert obtained_champion.champion_type2 is None
