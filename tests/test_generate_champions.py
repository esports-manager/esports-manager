import pytest

from src.resources.generator.generate_champions import ChampionGenerator


@pytest.fixture
def champion_generator():
    return ChampionGenerator()


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


def test_get_champions(champion_generator, tmpdir):
    temporary = tmpdir.mkdir()
    champion_generator.file_name = tmpdir.join('champions.json')
    champion_generator.create_champions_list()
    champion_generator.generate_file(temporary)
    champion_generator.get_champions(temporary)
    assert champion_generator.file_name.read_text() == champion_generator.champions_list


def test_generate_file(champion_generator, tmpdir):
    temporary = tmpdir.mkdir()
    champion_generator.file_name = tmpdir.join('champions.json')
    champion_generator.create_champions_list()
    champion_generator.generate_file(temporary)
    assert champion_generator.file_name.read_text() == champion_generator.champions_list
