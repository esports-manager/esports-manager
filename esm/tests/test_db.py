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
import json
from pathlib import Path

import pytest

from esm.core.db import DB
from esm.core.esports.moba.mobaregion import MobaRegion
from esm.core.esports.moba.mobateam import MobaPlayer, MobaTeam
from esm.core.utils import get_default_names_file, load_list_from_file


def test_generate_champion_files(
    db: DB, mock_champion_defs: list[dict[str, str | int | float]], tmp_path: Path
) -> None:
    moba_champions_path = tmp_path / "moba_champions.json"
    champions = db.generate_moba_champions(mock_champion_defs)
    expected_champions = db.serialize_champions(champions)
    db.generate_moba_file(moba_champions_path, expected_champions)
    assert moba_champions_path.exists()
    with moba_champions_path.open("r") as fp:
        actual_champions = json.load(fp)
    assert actual_champions == expected_champions


def test_generate_team_files(
    db: DB,
    mock_champion_defs: list[dict[str, str | int | float]],
    mock_moba_team_definitions,
    names_file: list[dict[str, dict[str, str | int]]],
    tmp_path: Path,
) -> None:
    teams_filepath = tmp_path / "moba_teams.json"
    champions = db.generate_moba_champions(mock_champion_defs)
    teams = db.generate_moba_teams(names_file, champions, mock_moba_team_definitions)
    serialized_teams = db.serialize_teams(teams)
    db.generate_moba_file(teams_filepath, serialized_teams)
    assert teams_filepath.exists()
    with teams_filepath.open("r") as fp:
        actual_teams = json.load(fp)
    assert actual_teams == serialized_teams


def test_get_players_from_teams(
    db: DB,
    mock_champion_defs: list[dict[str, str | int | float]],
    mock_moba_team_definitions,
    names_file: list[dict[str, dict[str, str | int]]],
    tmp_path: Path,
) -> None:
    champions = db.generate_moba_champions(mock_champion_defs)
    teams = db.generate_moba_teams(names_file, champions, mock_moba_team_definitions)
    players = db.get_moba_players_from_teams(teams)
    assert len(players) > 0
    assert all(isinstance(player, MobaPlayer) for player in players)


def test_generate_players_file(
    db: DB,
    mock_champion_defs: list[dict[str, str | int | float]],
    mock_moba_team_definitions,
    names_file: list[dict[str, dict[str, str | int]]],
    tmp_path: Path,
) -> None:
    players_filepath = tmp_path / "moba_players.json"
    champions = db.generate_moba_champions(mock_champion_defs)
    teams = db.generate_moba_teams(names_file, champions, mock_moba_team_definitions)
    players = db.get_moba_players_from_teams(teams)
    serialized_players = db.serialize_players(players)
    db.generate_moba_file(players_filepath, serialized_players)
    assert players_filepath.exists()
    with players_filepath.open("r", encoding="utf-8") as fp:
        actual_players = json.load(fp)
    assert actual_players == serialized_players


def test_get_team_definition_from_single_region_def(
    db: DB,
    tmp_path: Path,
) -> None:
    region_mock_files = [
        {
            "id": "testregion",
            "name": "TestRegion",
            "short_name": "TR",
            "filename": "testregion/teams.json",
        },
    ]
    mock_team_file = tmp_path / "testregion" / "teams.json"
    mock_team_file.parent.mkdir(parents=True)
    mock_team_file.touch()
    expected_mock_files = [
        {
            "id": "testregion",
            "name": "TestRegion",
            "short_name": "TR",
            "filename": mock_team_file.absolute().as_posix(),
        },
    ]
    assert (
        db.get_moba_region_definitions(region_mock_files, tmp_path)
        == expected_mock_files
    )


def test_get_team_definition_files_from_region_defs(
    db: DB,
    tmp_path: Path,
) -> None:
    region_mock_files = [
        {
            "id": "testregion",
            "name": "TestRegion",
            "short_name": "TR",
            "filename": "testregion/teams.json",
        },
        {
            "id": "testregion2",
            "name": "TestRegion2",
            "short_name": "TR2",
            "filename": "testregion2/teams2.json",
        },
    ]
    mock_team_file1 = tmp_path / "testregion" / "teams.json"
    mock_team_file2 = tmp_path / "testregion2" / "teams2.json"
    mock_team_file1.parent.mkdir(parents=True)
    mock_team_file2.parent.mkdir(parents=True)

    mock_team_file1.touch()
    mock_team_file2.touch()
    expected_mock_files = [
        {
            "id": "testregion",
            "name": "TestRegion",
            "short_name": "TR",
            "filename": mock_team_file1.absolute().as_posix(),
        },
        {
            "id": "testregion2",
            "name": "TestRegion2",
            "short_name": "TR2",
            "filename": mock_team_file2.absolute().as_posix(),
        },
    ]
    assert (
        db.get_moba_region_definitions(region_mock_files, tmp_path)
        == expected_mock_files
    )


def test_get_region_defs_non_existant_file(
    db: DB,
    tmp_path: Path,
) -> None:
    region_mock_files = [
        {
            "id": "testregion",
            "name": "TestRegion",
            "short_name": "TR",
            "filename": "testregion/teams.json",
        },
        {
            "id": "testregion2",
            "name": "TestRegion2",
            "short_name": "TR2",
            "filename": "testregion2/teams2.json",
        },
    ]
    with pytest.raises(FileNotFoundError):
        db.get_moba_region_definitions(region_mock_files, tmp_path)


def test_extract_teams_from_region_file(
    db: DB,
    mock_champion_defs: list[dict[str, str | int | float]],
    mock_moba_team_definitions,
    tmp_path: Path,
) -> None:
    mock_team_file = tmp_path / "testregion" / "teams.json"
    mock_team_file.parent.mkdir(parents=True)
    region_mock = {
        "id": "testregion",
        "name": "TestRegion",
        "short_name": "TR",
        "filename": mock_team_file.absolute().as_posix(),
    }

    with mock_team_file.open("w") as fp:
        json.dump(mock_moba_team_definitions, fp)

    champions = db.generate_moba_champions(mock_champion_defs)
    player_names = load_list_from_file(get_default_names_file())
    teams = db.extract_teams_from_region(region_mock, champions, player_names)

    assert len(teams) > 0
    assert all(isinstance(team, MobaTeam) for team in teams)
    for team in teams:
        for player in team.roster:
            assert isinstance(player, MobaPlayer)


def test_extract_regions_from_region_file(
    db: DB,
    mock_champion_defs: list[dict[str, str | int | float]],
    mock_moba_team_definitions,
    tmp_path: Path,
) -> None:
    mock_team_file1 = tmp_path / "testregion" / "teams.json"
    mock_team_file2 = tmp_path / "testregion2" / "teams.json"
    mock_team_file1.parent.mkdir(parents=True)
    mock_team_file2.parent.mkdir(parents=True)
    region_mock_file = [
        {
            "id": "testregion",
            "name": "TestRegion",
            "short_name": "TR",
            "filename": mock_team_file1.absolute().as_posix(),
        },
        {
            "id": "testregion2",
            "name": "TestRegion2",
            "short_name": "TR2",
            "filename": mock_team_file2.absolute().as_posix(),
        },
    ]

    with mock_team_file1.open("w", encoding="utf-8") as fp:
        json.dump(mock_moba_team_definitions, fp)

    with mock_team_file2.open("w", encoding="utf-8") as fp:
        json.dump(mock_moba_team_definitions, fp)

    champions = db.generate_moba_champions(mock_champion_defs)
    player_names = load_list_from_file(get_default_names_file())
    regions = db.extract_regions_from_region_file(
        region_mock_file, champions, player_names
    )
    assert len(regions) == 2
    assert all(isinstance(region, MobaRegion) for region in regions)
    for region in regions:
        for team in region.teams:
            assert isinstance(team, MobaTeam)
        assert len(region.teams) == len(mock_moba_team_definitions)


def test_generate_regions_file(
    db: DB,
    mock_champion_defs: list[dict[str, str | int | float]],
    mock_moba_team_definitions,
    names_file: list[dict[str, dict[str, str | int]]],
    tmp_path: Path,
):
    mock_team_file1 = tmp_path / "testregion" / "teams.json"
    mock_team_file2 = tmp_path / "testregion2" / "teams.json"
    mock_regions_file = tmp_path / "moba_regions.json"
    mock_team_file1.parent.mkdir(parents=True)
    mock_team_file2.parent.mkdir(parents=True)
    regions_def = [
        {
            "id": "testregion",
            "name": "TestRegion",
            "short_name": "TR",
            "filename": mock_team_file1.absolute().as_posix(),
        },
        {
            "id": "testregion2",
            "name": "TestRegion2",
            "short_name": "TR2",
            "filename": mock_team_file2.absolute().as_posix(),
        },
    ]

    with mock_team_file1.open("w", encoding="utf-8") as fp:
        json.dump(mock_moba_team_definitions, fp)

    with mock_team_file2.open("w", encoding="utf-8") as fp:
        json.dump(mock_moba_team_definitions, fp)

    regions_def = db.get_moba_region_definitions(regions_def, tmp_path)
    champions = db.generate_moba_champions(mock_champion_defs)
    regions = db.extract_regions_from_region_file(regions_def, champions, names_file)
    serialized_regions = db.serialize_regions(regions)
    db.generate_moba_file(mock_regions_file, serialized_regions)
    assert mock_regions_file.exists()
    with mock_regions_file.open("r") as fp:
        actual_regions = json.load(fp)
    assert actual_regions == serialized_regions
