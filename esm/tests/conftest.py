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
import uuid
from datetime import date

import pytest

from esm.core.db import DB
from esm.core.esports.moba.champion import Champion, ChampionDifficulty, ChampionType
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
from esm.core.settings import Settings
from esm.core.utils import load_list_from_file
from esm.definitions import ROOT_DIR


@pytest.fixture
def names_file() -> list[dict[str, str | float]]:
    filename = ROOT_DIR / "res" / "definitions" / "names.json"
    return load_list_from_file(filename)


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


@pytest.fixture
def mock_champions() -> list[Champion]:
    return [
        Champion(
            champion_id=uuid.uuid4(),
            name="Caitlyn",
            skill=60,
            scaling_factor=0.5,
            scaling_peak=20,
            lanes=LaneMultipliers(0.20, 0.10, 0.5, 1.00, 0.70),
            champion_difficulty=ChampionDifficulty.MEDIUM,
            champion_type1=ChampionType.MARKSMAN,
            champion_type2=None,
        ),
        Champion(
            champion_id=uuid.uuid4(),
            name="Kassadin",
            skill=70,
            scaling_factor=0.7,
            scaling_peak=25,
            lanes=LaneMultipliers(0.70, 0.10, 1.00, 0.05, 0.05),
            champion_difficulty=ChampionDifficulty.EASY,
            champion_type1=ChampionType.ASSASSIN,
            champion_type2=ChampionType.MAGE,
        ),
        Champion(
            champion_id=uuid.uuid4(),
            name="Soraka",
            skill=45,
            scaling_factor=0.2,
            scaling_peak=35,
            lanes=LaneMultipliers(0.60, 0.10, 0.05, 0.05, 1.00),
            champion_difficulty=ChampionDifficulty.EASY,
            champion_type1=ChampionType.HEALER,
            champion_type2=ChampionType.UTILITY,
        ),
        Champion(
            champion_id=uuid.uuid4(),
            name="K'Sante",
            skill=80,
            scaling_factor=0.9,
            scaling_peak=30,
            lanes=LaneMultipliers(1.00, 0.50, 1.00, 0.10, 0.60),
            champion_difficulty=ChampionDifficulty.MEDIUM,
            champion_type1=ChampionType.TANK,
            champion_type2=ChampionType.FIGHTER,
        ),
        Champion(
            champion_id=uuid.uuid4(),
            name="Lee Sin",
            skill=85,
            scaling_factor=0.4,
            scaling_peak=24,
            lanes=LaneMultipliers(0.80, 1.00, 0.60, 0.05, 0.05),
            champion_difficulty=ChampionDifficulty.HARD,
            champion_type1=ChampionType.FIGHTER,
            champion_type2=None,
        ),
        Champion(
            champion_id=uuid.uuid4(),
            name="Braum",
            skill=65,
            scaling_factor=0.3,
            scaling_peak=22,
            lanes=LaneMultipliers(0.05, 0.05, 0.05, 0.05, 1.00),
            champion_difficulty=ChampionDifficulty.EASY,
            champion_type1=ChampionType.TANK,
            champion_type2=ChampionType.UTILITY,
        ),
        Champion(
            champion_id=uuid.uuid4(),
            name="Twisted Fate",
            skill=85,
            scaling_factor=0.8,
            scaling_peak=28,
            lanes=LaneMultipliers(0.70, 0.10, 1.00, 0.80, 0.20),
            champion_difficulty=ChampionDifficulty.MEDIUM,
            champion_type1=ChampionType.MAGE,
            champion_type2=ChampionType.MARKSMAN,
        ),
        Champion(
            champion_id=uuid.uuid4(),
            name="Draven",
            skill=60,
            scaling_factor=0.7,
            scaling_peak=20,
            lanes=LaneMultipliers(0.20, 0.10, 0.5, 1.00, 0.70),
            champion_difficulty=ChampionDifficulty.HARD,
            champion_type1=ChampionType.MARKSMAN,
            champion_type2=None,
        ),
        Champion(
            champion_id=uuid.uuid4(),
            name="Gangplank",
            skill=70,
            scaling_factor=0.7,
            scaling_peak=20,
            lanes=LaneMultipliers(1.00, 0.10, 0.80, 0.10, 0.70),
            champion_difficulty=ChampionDifficulty.HARD,
            champion_type1=ChampionType.FIGHTER,
            champion_type2=None,
        ),
        Champion(
            champion_id=uuid.uuid4(),
            name="Kha'Zix",
            skill=54,
            scaling_factor=0.7,
            scaling_peak=26,
            lanes=LaneMultipliers(0.20, 1.00, 0.4, 0.05, 0.05),
            champion_difficulty=ChampionDifficulty.EASY,
            champion_type1=ChampionType.ASSASSIN,
            champion_type2=None,
        ),
    ]


@pytest.fixture
def mock_champion_defs() -> list[dict[str, str | int | float]]:
    return [
        {
            "name": "Caitlyn",
            "skill": 60,
            "scaling_factor ": 0.5,
            "scaling_peak": 20,
            "lanes": ["ADC"],
            "champion_difficulty": 1,
            "champion_type1": 4,
            "champion_type2": None,
        },
        {
            "name": "Kassadin",
            "skill": 70,
            "scaling_factor ": 0.7,
            "scaling_peak": 25,
            "lanes": ["JNG"],
            "champion_difficulty": 0,
            "champion_type1": 2,
            "champion_type2": 3,
        },
        {
            "name": "Soraka",
            "skill": 45,
            "scaling_factor ": 0.2,
            "scaling_peak": 35,
            "lanes": ["SUP"],
            "champion_difficulty": 0,
            "champion_type1": 6,
            "champion_type2": 5,
        },
        {
            "name": "K'Sante",
            "skill": 80,
            "scaling_factor ": 0.9,
            "scaling_peak": 30,
            "lanes": ["TOP", "MID"],
            "champion_difficulty": 1,
            "champion_type1": 0,
            "champion_type2": 1,
        },
        {
            "name": "Lee Sin",
            "skill": 85,
            "scaling_factor ": 0.4,
            "scaling_peak": 24,
            "lanes": ["JNG"],
            "champion_difficulty": 2,
            "champion_type1": 1,
            "champion_type2": None,
        },
        {
            "name": "Braum",
            "skill": 65,
            "scaling_factor": 0.3,
            "scaling_peak": 22,
            "lanes": ["SUP"],
            "champion_difficulty": 0,
            "champion_type1": 0,
            "champion_type2": 5,
        },
        {
            "name": "Twisted Fate",
            "skill": 85,
            "scaling_factor": 0.8,
            "scaling_peak": 28,
            "lanes": ["MID"],
            "champion_difficulty": 1,
            "champion_type1": 3,
            "champion_type2": 4,
        },
        {
            "name": "Draven",
            "skill": 60,
            "scaling_factor": 0.7,
            "scaling_peak": 20,
            "lanes": ["ADC"],
            "champion_difficulty": 2,
            "champion_type1": 4,
            "champion_type2": None,
        },
        {
            "name": "Gangplank",
            "skill": 70,
            "scaling_factor": 0.7,
            "scaling_peak": 20,
            "lanes": ["TOP"],
            "champion_difficulty": 2,
            "champion_type1": 1,
            "champion_type2": None,
        },
        {
            "name": "Kha'Zix",
            "skill": 54,
            "scaling_factor": 0.7,
            "scaling_peak": 26,
            "lanes": ["JNG"],
            "champion_difficulty": 0,
            "champion_type1": 2,
            "champion_type2": None,
        },
    ]


@pytest.fixture
def settings(tmp_path) -> Settings:
    root_dir = tmp_path / "esm"
    settings = Settings(root_dir)
    return settings


@pytest.fixture
def db(settings: Settings) -> DB:
    return DB(settings)
