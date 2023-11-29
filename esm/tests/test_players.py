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
import uuid

import pytest

from esm.core.esports.moba.player import (
    MobaPlayer,
)


@pytest.fixture
def player_dict(lanes, attributes, moba_player_champions) -> dict:
    return {
        "id": uuid.UUID(int=1).hex,
        "nationality": "United States",
        "first_name": "PlayerName",
        "last_name": "PlayerSurname",
        "birthday": "2001-01-01",
        "nick_name": "NickName",
        "lanes": lanes.serialize(),
        "attributes": attributes.serialize(),
        "champion_pool": [champion.serialize() for champion in moba_player_champions],
    }


def test_serialize_player(player, player_dict):
    assert player.serialize() == player_dict


def test_player_get_from_dict(player, player_dict):
    assert MobaPlayer.get_from_dict(player_dict) == player


def test_player_str(player):
    assert player.__str__() == "NickName"
