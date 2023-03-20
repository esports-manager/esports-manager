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
import uuid
from datetime import date

from esm.core.esports.moba.player import MobaPlayer, MobaPlayerAttributes, MobaPlayerSimulator, MobaPlayerChampion
from esm.core.esports.moba.champion import Champion
from esm.core.esports.moba.moba_definitions import LaneMultipliers


@pytest.fixture
def lanes() -> LaneMultipliers:
    return LaneMultipliers(0.5, 0.8, 0.4, 1.0, 0.0)


@pytest.fixture
def attributes() -> MobaPlayerAttributes:
    return MobaPlayerAttributes(75, 85, 87, 86, 49, 91, 95, 82, 90, 89, 84, 85)


@pytest.fixture
def champions() -> list[MobaPlayerChampion]:
    return [
        MobaPlayerChampion(uuid.uuid4(), 0.6),
        MobaPlayerChampion(uuid.uuid4(), 0.7),
        MobaPlayerChampion(uuid.uuid4(), 0.8),
        MobaPlayerChampion(uuid.uuid4(), 0.9),
        MobaPlayerChampion(uuid.uuid4(), 1.0),
    ]


@pytest.fixture
def player(lanes, attributes, champions) -> MobaPlayer:
    return MobaPlayer(
        uuid.UUID(int=1),
        "United States",
        "PlayerName",
        "PlayerSurname",
        date(2001, 1, 1),
        "NickName",
        lanes,
        attributes,
        champions,
    )


@pytest.fixture
def player_dict(lanes, attributes, champions) -> dict:
    return {
        "id": uuid.UUID(int=1).hex,
        "nationality": "United States",
        "first_name": "PlayerName",
        "last_name": "PlayerSurname",
        "birthday": "2001-01-01",
        "nick_name": "NickName",
        "lanes": lanes.serialize(),
        "attributes": attributes.serialize(),
        "champions": [champion.serialize() for champion in champions]
    }


def test_serialize_player(player, player_dict):
    assert player.serialize() == player_dict


def test_player_get_from_dict(player, player_dict):
    assert MobaPlayer.get_from_dict(player_dict) == player


def test_player_str(player):
    assert player.__str__() == "NickName"


