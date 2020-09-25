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

import PySimpleGUI as sg
import asyncio

from src.ui.gui import app, debug_window
from src.resources.utils import find_file
from src.resources.generator.generate_champions import generate_champion_file, create_champions_list
from src.resources.generator.generate_teams import generate_team_file
from src.resources.generator.generate_players import generate_player_file
from src.core.match_live import debug_match


def generation():
    players = []
    champions = create_champions_list()
    generate_champion_file()
    generate_team_file(players)
    generate_player_file(players)


async def testing_match():
    window = debug_window()
    while True:
        event, values = window.read()
        if event in [sg.WINDOW_CLOSED, 'exit_main']:
            break

    window.close()


if __name__ == '__main__':
    try:
        find_file('champions.json')
        find_file('players.json')
        find_file('teams.json')
    except FileNotFoundError:
        generation()

    app()
