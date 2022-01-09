import pytest

from esm.core.settings import Settings
from esm.definitions import *


@pytest.fixture
def settings(tmpdir):
    settings = Settings()
    settings.config_file = tmpdir.join('config.yaml')
    settings.create_config_file()
    return settings


def test_get_data(settings):
    expected_data = {
        "font_scale": 1,
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


