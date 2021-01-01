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
import threading
import random
import PySimpleGUI as sg
import uuid

from src.core.esports.moba.match_live import initialize_match
from src.resources.generator.generate_players import MobaPlayerGenerator
from src.resources.generator.generate_teams import TeamGenerator
from src.resources.generator.generate_champions import ChampionGenerator
from src.core.esports.moba.mobaevent import MobaEventHandler
from src.ui.gui import debug_window, get_team_data


def match_simulation_thread(match, window):
    match.simulation()
    window.write_event_value('MATCH SIMULATED', 'DONE')
    window.Element('-StartMatch-').Update(disabled=False)
    window.Element('-NewTeams-').Update(disabled=False)


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

    match = initialize_match(team1, team2, uuid.uuid4())
    match.picks_and_bans()

    return match


def update_info(match, window, data):
    window.Element('-Team1Table-').update(values=data[0])
    window.Element('-Team2Table-').update(values=data[1])
    window.Element('team1skill').update(value=match.match.team1.total_skill)
    window.Element('team2skill').update(value=match.match.team2.total_skill)
    window.Element('team1winprob').Update(value=match.match.team1.win_prob)
    window.Element('team2winprob').Update(value=match.match.team2.win_prob)
    window.Element('team1towers').Update(value=match.match.team1.towers)
    window.Element('team2towers').Update(value=match.match.team2.towers)
    window.Element('team1inhibs').Update(value=match.match.team1.inhibitors)
    window.Element('team2inhibs').Update(value=match.match.team2.inhibitors)
    window.Element('team1name').Update(value=match.match.team1.name)
    window.Element('team2name').Update(value=match.match.team2.name)
    window.refresh()


def match_debugger():
    match = get_match()
    window = debug_window(match)

    while True:
        event, values = window.read(timeout=100)

        if event in [sg.WINDOW_CLOSED, 'exit_main']:
            break

        elif event == '-StartMatch-':
            match.is_match_over = False
            match.game_time = 0.0
            match.event_handler = MobaEventHandler()
            for team in match.match.teams:
                for player in team.list_players:
                    player.kills = 0
                    player.deaths = 0
                    player.assists = 0
                    player.points = 0
                team.towers.update(
                    {
                        "top": 3,
                        "mid": 3,
                        "bot": 3,
                        "base": 2
                    }
                )
                team.inhibitors.update(
                    {
                        "top": 1,
                        "mid": 1,
                        "bot": 1
                    }
                )
                team.nexus = 1
            try:
                thread = threading.Thread(target=match_simulation_thread, args=(match, window), daemon=True)
                thread.start()
                window.Element('-StartMatch-').Update(disabled=True)
                window.Element('-NewTeams-').Update(disabled=True)
            except Exception as e:
                print('Error starting thread.')

        elif event == '-NewTeams-':
            match = get_match()
            data = get_team_data(match)
            update_info(match, window, data)

        data = get_team_data(match)
        update_info(match, window, data)
    window.close()
