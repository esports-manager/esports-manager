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
import cbor2
import pytest

from esm.core.esports.moba.generator import ChampionGenerator
from esm.core.esports.moba.generator import MobaPlayerGenerator
from esm.core.esports.moba.generator import TeamGenerator
from esm.core.save_load import SaveGame, LoadGame, LoadGameError
from esm.core.gamestate import GameState


@pytest.fixture()
def load_game_dir(tmpdir):
    return tmpdir.mkdir('save')


@pytest.fixture()
def load_game(load_game_dir):
    load_game = LoadGame(load_game_dir)
    return load_game


@pytest.fixture()
def save_game_file(load_game_dir):
    return load_game_dir.join('testgame1.cbor')


@pytest.fixture()
def save_game(gamestate, load_game_dir, save_game_file):
    save_game = SaveGame(gamestate, save_game_file, save_directory=load_game_dir, autosave_enabled=False)
    return save_game


@pytest.fixture()
def champions_list():
    champions = ChampionGenerator()
    champions.generate_champions()
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
def gamestate(teams_list, players, champions_list, save_game_file):
    return GameState(
        'TestGame1',
        save_game_file,
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


def test_key_integrity(save_game, load_game, save_game_file):
    save_game.save_game()
    # Write this to raise the error
    with open(save_game_file, 'rb+') as fp:
        data = cbor2.load(fp)
        data["unknown_attr"] = 'fail_test'
        cbor2.dump(data, fp)

    with pytest.raises(LoadGameError):
        load_game.load_game_state(save_game_file)
