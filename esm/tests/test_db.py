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
import datetime

from uuid import UUID
from esm.core.db import DB
from esm.core.settings import Settings
from esm.core.esports.moba.team import Team
from esm.core.esports.moba.player import MobaPlayer


@pytest.fixture
def settings(tmp_path):
    root_dir = tmp_path / "root"
    root_dir.mkdir()
    db_dir = tmp_path / "dir"
    db_dir.mkdir()
    save_file_dir = root_dir / "save"
    save_file_dir.mkdir()
    champions_file = db_dir / "champions.json"
    players_file = db_dir / "players.json"
    teams_file = db_dir / "teams.json"
    config_file = root_dir / 'config.yaml'
    settings = Settings(
        root_dir=root_dir,
        db_dir=db_dir,
        save_file_dir=save_file_dir,
        champions_file=champions_file,
        players_file=players_file,
        teams_file=teams_file,
        config_file=config_file
    )
    settings.create_config_file()
    return settings


@pytest.fixture
def db(settings) -> DB:
    return DB(settings)


def test_db_load_moba_teams(db):
    db.generate_moba_files()
    teams = db.load_moba_teams()
    for team in teams:
        assert isinstance(team, Team)
        assert isinstance(team.team_id, UUID)
        assert team.list_players is not None
        for player in team.list_players:
            assert isinstance(player, MobaPlayer)
            assert isinstance(player.player_id, UUID)
            assert isinstance(player.birthday, datetime.date)
            for champion in player.champions:
                assert isinstance(champion, dict)
