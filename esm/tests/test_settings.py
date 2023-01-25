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

from esm.core.settings import Settings
from esm.definitions import *


@pytest.fixture
def settings(tmp_path):
    settings = Settings()
    settings.config_file = tmp_path / 'config.yaml'
    settings.create_config_file()
    return settings


def test_get_data(settings):
    expected_data = {
        "font_scale": 1,
        "amount_players": 50,
        "enable_auto_save": True,
        "root_dir": ROOT_DIR,
        "res_dir": RES_DIR,
        "db_dir": DB_DIR,
        "save_file_dir": SAVE_FILE_DIR,
        "champions_file": CHAMPIONS_FILE,
        "players_file": PLAYERS_FILE,
        "teams_file": TEAMS_FILE,
    }
    data = settings.load_config_file()
    settings.parse_config_file(data)
    assert settings.get_data() == expected_data
