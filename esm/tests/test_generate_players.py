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

from esm.core.esports.moba.generator.default_champion_defs import (
    get_default_champion_defs,
)
from esm.core.esports.moba.generator.generate_players import MobaPlayerGenerator, MobaPlayerAttributesGeneratorError, MobaPlayerGeneratorError
from esm.core.esports.moba.generator.generate_champions import ChampionGenerator
from esm.core.esports.moba.player import MobaPlayer
from esm.core.utils import load_list_from_file
from esm.definitions import NAMES_FILE


@pytest.fixture
def moba_player_gen() -> MobaPlayerGenerator:
    champions_gen = ChampionGenerator(get_default_champion_defs())
    champions = champions_gen.generate()
    names = load_list_from_file(NAMES_FILE)
    return MobaPlayerGenerator(champions, names)


def test_generate_default_mobaplayer(moba_player_gen: MobaPlayerGenerator):
    players = moba_player_gen.generate()
    assert len(players) == 5
    for player in players:
        assert isinstance(player, MobaPlayer)


def test_generate_rand_mobaplayer(moba_player_gen: MobaPlayerGenerator):
    players = moba_player_gen.generate(rand=True)
    assert len(players) == 5
    for player in players:
        assert isinstance(player, MobaPlayer)


def test_raises_error_if_amount_is_not_divisible_by_five(moba_player_gen: MobaPlayerGenerator):
    with pytest.raises(MobaPlayerGeneratorError):
        players = moba_player_gen.generate(amount=1)
    