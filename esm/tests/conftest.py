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
from datetime import date, datetime
from pathlib import Path

import pytest

from esm.core.db import DB
from esm.core.esports.moba.champion import Champion, ChampionDifficulty, ChampionType
from esm.core.esports.moba.generator import ChampionGenerator, MobaTeamGenerator
from esm.core.esports.moba.moba_definitions import LaneMultipliers, Lanes
from esm.core.esports.moba.mobamatch import MobaMatch
from esm.core.esports.moba.mobaplayer import (
    ChampionMastery,
    CommunicationAttributes,
    KnowledgeAttributes,
    MechanicsAttributes,
    MobaPlayer,
    MobaPlayerAttributes,
    MobaPlayerChampion,
    MobaPlayerSimulation,
    OffensiveAttributes,
    UtilityAttributes,
)
from esm.core.esports.moba.mobateam import MobaTeam, MobaTeamSimulation
from esm.core.esports.moba.simulation.moba_sim_match import MobaSimMatch
from esm.core.esports.moba.simulation.picksbans import PicksBans
from esm.core.settings import Settings
from esm.core.utils import get_default_names_file, load_list_from_file
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
            Lanes.TOP.name: 0.80,
            Lanes.JNG.name: 1.00,
            Lanes.MID.name: 0.45,
            Lanes.ADC.name: 0.30,
            Lanes.SUP.name: 0.10,
        },
        "scaling_factor": 0.5,
        "scaling_peak": 20,
        "skill": 87,
        "difficulty": ChampionDifficulty.MEDIUM.value,
        "type1": ChampionType.TANK.value,
        "type2": ChampionType.FIGHTER.value,
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
def mock_champion_defs() -> list[dict[str, str | int | float]]:
    filename = (
        ROOT_DIR / "res" / "definitions" / "moba" / "champions" / "champions.json"
    )
    return load_list_from_file(filename)


@pytest.fixture
def mock_champions(
    mock_champion_defs: list[dict[str, str | int | float]]
) -> list[Champion]:
    champion_gen = ChampionGenerator()
    return [champion_gen.generate(champion_def) for champion_def in mock_champion_defs]


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    settings = Settings()
    settings.db_dir = tmp_path / "db"
    return settings


@pytest.fixture
def db() -> DB:
    return DB()


@pytest.fixture
def mock_moba_team_definitions() -> list[dict[str, int | str]]:
    return [
        {
            "name": "KoreanTeam",
            "nationality": "Korea",
            "mu": 88,
            "sigma": 15,
        },
        {
            "name": "GermanTeam",
            "nationality": "Germany",
            "mu": 75,
            "sigma": 20,
        },
        {
            "name": "ChineseTeam",
            "nationality": "China",
            "mu": 89,
            "sigma": 10,
        },
    ]


@pytest.fixture
def mock_moba_teams(
    mock_moba_team_definitions, mock_champions: list[Champion]
) -> list[MobaTeam]:
    names = load_list_from_file(get_default_names_file())
    teams = [
        MobaTeamGenerator(mock_champions, player_names=names).generate(team_def)
        for team_def in mock_moba_team_definitions
    ]
    return teams


@pytest.fixture
def moba_match(mock_moba_teams: list[MobaTeam]) -> MobaMatch:
    return MobaMatch(
        uuid.uuid4(),
        uuid.uuid4(),
        mock_moba_teams[0],
        mock_moba_teams[1],
        datetime.strptime("2020-01-01, 10:00", "%Y-%m-%d, %H:%M"),
        None,
    )


@pytest.fixture
def moba_match_simulation(moba_match: MobaMatch) -> MobaSimMatch:
    team1 = moba_match.team1
    team2 = moba_match.team2
    team1_players = [
        MobaPlayerSimulation(pl, Lanes(i))
        for i, pl in zip(list(Lanes), team1.roster[:5])
    ]
    team2_players = [
        MobaPlayerSimulation(pl, Lanes(i))
        for i, pl in zip(list(Lanes), team2.roster[:5])
    ]
    team1_sim = MobaTeamSimulation(team1, team1_players, False)
    team2_sim = MobaTeamSimulation(team2, team2_players, False)
    return MobaSimMatch(moba_match, team1_sim, team2_sim)


@pytest.fixture
def moba_picks_bans(
    moba_match_simulation: MobaSimMatch, mock_champions: list[Champion]
) -> PicksBans:
    team1 = moba_match_simulation.team1
    team2 = moba_match_simulation.team2
    return PicksBans(mock_champions, team1, team2)
