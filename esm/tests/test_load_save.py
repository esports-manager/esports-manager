import pytest

from datetime import datetime
from esm.core.generator.generate_teams import TeamGenerator
from esm.core.generator.generate_champions import ChampionGenerator
from esm.core.generator.generate_players import MobaPlayerGenerator
from esm.core.gamestate import GameState
from esm.core.load_game import LoadGame
from esm.core.save_game import SaveGame


@pytest.fixture()
def load_game_dir(tmpdir):
    return tmpdir.mkdir('save')


@pytest.fixture()
def load_game(load_game_dir):
    return LoadGame(load_game_dir)


@pytest.fixture()
def save_game_file(load_game_dir):
    return load_game_dir.join('testgame1')


@pytest.fixture()
def save_game(save_game_file, gamestate, load_game_dir):
    return SaveGame(gamestate, save_game_file, save_directory=load_game_dir, autosave_enabled=False)


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
        'testgame1',
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
