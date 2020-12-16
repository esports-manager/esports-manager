#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020  Pedrenrique G. Guimarães
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

#import PySimpleGUI as sg

# from src.ui.gui import app, debug_window
from src.resources.utils import find_file
from src.resources.generator.generate_champions import ChampionGenerator
from src.resources.generator.generate_teams import TeamGenerator
from src.resources.generator.generate_players import MobaPlayerGenerator
from src.core.esports.moba.debug import match_debugger


def generation():
    num_players = 3500
    num_teams = int(num_players / 5)

    champions = ChampionGenerator()
    champions.get_champion_names()
    champions.create_champions_list()
    player_gen = MobaPlayerGenerator(lane=0, champions_list=champions.champions_obj)
    player_gen.generate_players(num_players)
    team_gen = TeamGenerator(players=player_gen.players, organized=True, amount=num_teams)
    team_gen.generate_teams()

    champions.generate_file()
    player_gen.generate_file()
    team_gen.generate_file()


def debug_match():
    match_debugger()


if __name__ == '__main__':
    # try:
    #     find_file('champions.json')
    #     find_file('players.json')
    #     find_file('teams.json')
    # except FileNotFoundError():
    #     generation()

    generation()

    debug_match()
