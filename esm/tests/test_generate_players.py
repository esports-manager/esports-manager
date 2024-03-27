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
import hypothesis.strategies as st
from hypothesis import given

from esm.core.esports.moba.champion import (
    Champion,
    ChampionDifficulty,
    ChampionType,
    LaneMultipliers,
)
from esm.core.esports.moba.generator.generate_players import Lanes, MobaPlayerGenerator
from esm.core.esports.moba.player import MobaPlayer
from esm.core.utils import get_default_names_file, load_list_from_file

ch = st.lists(
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
    ),
    min_size=1,
    max_size=10,
)


@given(ch)
def test_generate_default_mobaplayer(champions: list[Champion]):
    names = load_list_from_file(get_default_names_file())
    moba_player_gen = MobaPlayerGenerator(champions_list=champions, names=names)
    for lane in Lanes:
        player = moba_player_gen.generate(lane=lane)
        assert isinstance(player, MobaPlayer)


@given(ch)
def test_generate_rand_mobaplayer(champions: list[Champion]):
    names = load_list_from_file(get_default_names_file())
    moba_player_gen = MobaPlayerGenerator(champions_list=champions, names=names)
    players = [moba_player_gen.generate(lane=Lanes(i)) for i in range(5)]
    assert len(players) == 5
    for player in players:
        assert isinstance(player, MobaPlayer)
