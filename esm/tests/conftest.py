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

import hypothesis.strategies as st
import pytest
from hypothesis import given

from esm.core.esports.moba.champion import Champion, ChampionDifficulty, ChampionType
from esm.core.esports.moba.generator.generate_players import MobaPlayerGenerator
from esm.core.esports.moba.moba_definitions import LaneMultipliers, Lanes
from esm.core.esports.moba.player import (
    ChampionMastery,
    CommunicationAttributes,
    KnowledgeAttributes,
    MechanicsAttributes,
    MobaPlayer,
    MobaPlayerAttributes,
    MobaPlayerChampion,
    OffensiveAttributes,
    UtilityAttributes,
)
from esm.core.utils import load_list_from_file
from esm.definitions import NAMES_FILE


@pytest.fixture
def champion():
    lanes = LaneMultipliers(0.80, 1.00, 0.45, 0.30, 0.10)
    return Champion(
        uuid.UUID(int=1),
        "MyChampion",
        87,
        0.5,
        20,
        lanes,
        ChampionDifficulty.MEDIUM,
        ChampionType.TANK,
        ChampionType.FIGHTER,
    )


@pytest.fixture
def champion_dict():
    return {
        "id": "00000000000000000000000000000001",
        "name": "MyChampion",
        "lanes": {
            Lanes.TOP.value: 0.80,
            Lanes.JNG.value: 1.00,
            Lanes.MID.value: 0.45,
            Lanes.ADC.value: 0.30,
            Lanes.SUP.value: 0.10,
        },
        "scaling_factor": 0.5,
        "scaling_peak": 20,
        "skill": 87,
        "champion_difficulty": ChampionDifficulty.MEDIUM.value,
        "champion_type1": ChampionType.TANK.value,
        "champion_type2": ChampionType.FIGHTER.value,
    }


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
def moba_player_champions() -> list[MobaPlayerChampion]:
    return [
        MobaPlayerChampion(uuid.uuid4(), ChampionMastery.GOLD, 0.0),
        MobaPlayerChampion(uuid.uuid4(), ChampionMastery.DIAMOND, 100.0),
        MobaPlayerChampion(uuid.uuid4(), ChampionMastery.PLATINUM, 50.0),
        MobaPlayerChampion(uuid.uuid4(), ChampionMastery.SILVER, 1239.0),
        MobaPlayerChampion(uuid.uuid4(), ChampionMastery.MASTER, 1000.0),
        MobaPlayerChampion(uuid.uuid4(), ChampionMastery.GRANDMASTER, 0.0),
    ]


@pytest.fixture
def player(lanes, attributes, moba_player_champions) -> MobaPlayer:
    return MobaPlayer(
        uuid.UUID(int=1),
        "United States",
        "PlayerName",
        "PlayerSurname",
        date(2001, 1, 1),
        "NickName",
        lanes,
        attributes,
        moba_player_champions,
    )
