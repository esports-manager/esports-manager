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
from esm.core.esports.moba.champion import Champion
from esm.core.esports.moba.generator.generate_players import Lanes, MobaPlayerGenerator
from esm.core.esports.moba.mobaplayer import MobaPlayer
from esm.core.utils import get_default_names_file, load_list_from_file


def test_generate_default_moba_player(mock_champions: list[Champion]):
    names = load_list_from_file(get_default_names_file())
    moba_player_gen = MobaPlayerGenerator(champions_list=mock_champions, names=names)
    for lane in Lanes:
        player = moba_player_gen.generate(lane=lane)
        assert isinstance(player, MobaPlayer)


def test_generate_rand_moba_player(mock_champions: list[Champion]):
    names = load_list_from_file(get_default_names_file())
    moba_player_gen = MobaPlayerGenerator(champions_list=mock_champions, names=names)
    players = [moba_player_gen.generate(lane=Lanes(i)) for i in list(Lanes)]
    assert len(players) == 5
    for player in players:
        assert isinstance(player, MobaPlayer)
