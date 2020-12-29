import pytest

from src.resources.generator.generate_champions import ChampionGenerator


@pytest.fixture
def champion_generator():
    pass


def test_get_champion_lanes(champion_generator):
    pass


def test_generate_champion_skill(champion_generator):
    pass


def test_generate_champion_dict(champion_generator):
    pass


def test_generate_champion_obj(champion_generator):
    pass


def test_create_champions_list(champion_generator):
    pass


def test_get_champions(champion_generator):
    pass


def test_generate_file(champion_generator, tmp_path):
    tmp_path.mkdir()
    champion_generator.file_name = tmp_path / 'champions.json'
    champion_generator.create_champions_list()
    champion_generator.generate_file()
    assert champion_generator.file_name.read_text() != champion_generator.champions_list
