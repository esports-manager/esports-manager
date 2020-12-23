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

import random
import PySimpleGUI as sg
import uuid

from src.core.esports.moba.match_live import MatchLive, initialize_match
from src.resources.generator.generate_players import MobaPlayerGenerator
from src.resources.generator.generate_teams import TeamGenerator
from src.resources.generator.generate_champions import ChampionGenerator
from src.resources.utils import load_list_from_json
from src.ui.gui import debug_window, get_team_data


def get_match():
    ch = ChampionGenerator()
    pl = MobaPlayerGenerator()
    t = TeamGenerator()

    pl.get_players_dict()
    pl.get_players_objects()
    ch.get_champions()

    t.player_list = pl.players
    t.get_teams_dict()
    t.get_teams_objects()

    team1 = random.choice(t.teams)
    t.teams.remove(team1)
    team2 = random.choice(t.teams)
    t.teams.remove(team2)

    print(team1.list_players)
    print(team2.list_players)

    match = initialize_match(team1, team2, uuid.uuid4())
    match.picks_and_bans()

    return match


def match_debugger():
    match = get_match()
    window = debug_window(match)

    while True:
        event, values = window.read()
        if event in [sg.WINDOW_CLOSED, 'exit_main']:
            break
        elif event == '-StartMatch-':
            match.is_match_over = False
            match.game_time = 0.0
            for team in match.match.teams:
                for player in team.list_players:
                    player.kills = 0
                    player.deaths = 0
                    player.assists = 0
                team.total_skill
            match.simulation()
        elif event == '-NewTeams-':
            match = get_match()
            data = get_team_data(match)
            window.Element('-Team1Table-').Update(values=data[0])
            window.Element('-Team2Table-').Update(values=data[1])
            window.Element('team1skill').Update(value=match.match.team1.total_skill)
            window.Element('team2skill').Update(value=match.match.team2.total_skill)

        data = get_team_data(match)
        window.Element('-Team1Table-').update(values=data[0])
        window.Element('-Team2Table-').update(values=data[1])
        window.Element('team1skill').update(value=match.match.team1.total_skill)
        window.Element('team2skill').update(value=match.match.team2.total_skill)

    window.close()
