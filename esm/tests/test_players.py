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
from datetime import date

import pytest

from esm.core.esports.moba.moba_definitions import LaneMultipliers
from esm.core.esports.moba.player import (
    MobaPlayer,
    MobaPlayerAttributes,
    OffensiveAttributes,
    MechanicsAttributes,
    UtilityAttributes,
    KnowledgeAttributes,
    CommunicationAttributes,
    ChampionMastery,
    MobaPlayerChampion,
)


@pytest.fixture
def lanes() -> LaneMultipliers:
    return LaneMultipliers(0.5, 0.8, 0.4, 1.0, 0.0)


@pytest.fixture
def attributes() -> MobaPlayerAttributes:
    offensive = OffensiveAttributes(80, 85, 91)
    communication = CommunicationAttributes(80, 85, 91)
    mechanics = MechanicsAttributes(90, 89, 86, 95, 78, 88)
    knowledge = KnowledgeAttributes(80, 85, 91)
    utility = UtilityAttributes(80, 90, 78)

    return MobaPlayerAttributes(
        offensive,
        communication,
        mechanics,
        knowledge,
        utility,
    )


@pytest.fixture
def champions() -> list[MobaPlayerChampion]:
    return [
        MobaPlayerChampion(uuid.uuid4(), ChampionMastery.GOLD, 0.0),
        MobaPlayerChampion(uuid.uuid4(), ChampionMastery.DIAMOND, 100.0),
        MobaPlayerChampion(uuid.uuid4(), ChampionMastery.PLATINUM, 50.0),
        MobaPlayerChampion(uuid.uuid4(), ChampionMastery.SILVER, 1239.0),
        MobaPlayerChampion(uuid.uuid4(), ChampionMastery.MASTER, 1000.0),
        MobaPlayerChampion(uuid.uuid4(), ChampionMastery.GRANDMASTER, 0.0),
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
        "champion_pool": [champion.serialize() for champion in champions],
    }


def test_serialize_player(player, player_dict):
    assert player.serialize() == player_dict


def test_player_get_from_dict(player, player_dict):
    assert MobaPlayer.get_from_dict(player_dict) == player


def test_player_str(player):
    assert player.__str__() == "NickName"
