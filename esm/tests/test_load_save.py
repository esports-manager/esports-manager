import pytest
import cbor2

from esm.core.gamestate import GameState
from esm.core.hashfile import HashFile
from esm.core.generator.generate_champions import ChampionGenerator
from esm.core.generator.generate_players import MobaPlayerGenerator
from esm.core.generator.generate_teams import TeamGenerator
from esm.core.load_game import LoadGame, LoadGameError
from esm.core.save_game import SaveGame


@pytest.fixture()
def hash_file(tmp_path):
    hash_file = HashFile()
    d = tmp_path / "hashes"
    d.mkdir()
    p = d / "hash_file.cbor"
    with open(p, "wb") as fp:
        cbor2.dump({}, fp)
    hash_file.filename = p
    return hash_file


@pytest.fixture()
def load_game_dir(tmpdir):
    return tmpdir.mkdir('save')


@pytest.fixture()
def load_game(load_game_dir, hash_file):
    load_game = LoadGame(load_game_dir)
    load_game.hash_file = hash_file
    return load_game


@pytest.fixture()
def save_game_file(load_game_dir):
    return load_game_dir.join('testgame1.cbor')


@pytest.fixture()
def save_game(save_game_file, gamestate, load_game_dir, hash_file):
    save_game = SaveGame(gamestate, save_game_file, save_directory=load_game_dir, autosave_enabled=False)
    save_game.hash_file = hash_file
    return save_game


@pytest.fixture()
def champions_list():
    champions = ChampionGenerator()
    champions.create_champions_list()
    return champions.champions_list


@pytest.fixture()
def players(champions_list):
    players = MobaPlayerGenerator(champions_list=champions_list)
    players.generate_players(amount=25)
    return players


@pytest.fixture()
def teams_list(players):
    team_gen = TeamGenerator(players=players.players)
    team_gen.generate_teams()
    return team_gen.teams_dict


@pytest.fixture()
def gamestate(teams_list, players, champions_list):
    return GameState(
        'TestGame1',
        'testgame1.cbor',
        {
            'name': 'TestManager',
            'birthday': '1995/02/01',
            'team': 1,
            'quality': 50,
        },
        '2020',
        'MOBA',
        teams_list,
        players.players_dict,
        champions_list
    )


def test_save_load_game(save_game, load_game, save_game_file):
    save_game.save_game()
    assert save_game.gamestate == load_game.load_game_state(save_game_file)


def test_hash_file(save_game, load_game, save_game_file):
    save_game.save_game()
    assert save_game.hash_file == load_game.hash_file
    assert save_game.hash_file.hash_data == load_game.hash_file.hash_data
    assert load_game.check_game_file(save_game_file) is True


def test_key_integrity(save_game, load_game, save_game_file):
    save_game.save_game()
    # Write this to raise the error
    with open(save_game_file, 'rb+') as fp:
        data = cbor2.load(fp)
        data["unknown_attr"] = 'fail_test'
        cbor2.dump(data, fp)

    with pytest.raises(LoadGameError):
        load_game.load_game_state(save_game_file)
