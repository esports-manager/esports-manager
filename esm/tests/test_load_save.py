import pytest

from esm.core.generator.generate_teams import TeamGenerator
from esm.core.generator.generate_champions import ChampionGenerator
from esm.core.generator.generate_players import MobaPlayerGenerator
from esm.core.gamestate import GameState
from esm.core.load_game import LoadGame
from esm.core.save_game import SaveGame


@pytest.fixture
def load_game(tmpdir):
    temporary = tmpdir.mkdir('save')
    return LoadGame(temporary)


@pytest.fixture
def champions_list():
    champions = ChampionGenerator()
    champions.create_champions_list()
    return champions.champions_list


@pytest.fixture
def players(champions_list):
    players = MobaPlayerGenerator(champions_list=champions_list)
    players.generate_players(amount=25)
    return players


@pytest.fixture
def teams_list(players):
    team_gen = TeamGenerator(players=players.players)
    team_gen.generate_teams()
    return team_gen.teams_dict


@pytest.fixture
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
