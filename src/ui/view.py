#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2021  Pedrenrique G. Guimarães
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

from src.core.esports.moba.match_live import MatchLive
from .gui import GUI


class View:
    def __init__(self, controller):
        self.gui = GUI(controller)
        self.controller = controller
        self.is_match_running = False

    def print_error(self, e):
        self.gui.error_message(e)

    def print_generate_data_window(self, players, teams, champions):
        self.gui.generate_data_window(players, teams, champions)

    def make_screen_visible(self, inv_screen, vis_screen):
        self.gui.window[inv_screen].update(visible=False)
        self.gui.window[vis_screen].update(visible=True)

    def disable_debug_buttons(self):
        self.gui.window.Element('debug_startmatch_btn').Update(disabled=True)
        self.gui.window.Element('debug_newteams_btn').Update(disabled=True)
        self.gui.window.Element('debug_resetmatch_btn').Update(disabled=True)

    def update_match_sim_elements(self):
        self.gui.window.write_event_value('MATCH SIMULATED', 'DONE')
        self.gui.window.Element('debug_startmatch_btn').Update(disabled=False)
        self.gui.window.Element('debug_newteams_btn').Update(disabled=False)
        self.gui.window.Element('debug_resetmatch_btn').Update(disabled=False)

    def team_data(self, match_live):
        players = [[player for player in team.list_players] for team in match_live.match.teams]

        # Event handler shuffles players, this keeps them in order
        for team in players:
            team.sort(key=lambda x: x.lane.value)

        data = []
        for team in players:
            team_data = [
                [
                    player.lane.name,
                    player.nick_name,
                    player.kills,
                    player.deaths,
                    player.assists,
                    player.champion,
                    int(player.get_player_total_skill())
                ] for player in team
            ]
            data.append(team_data)

        return data

    def start(self):
        match_live = None

        while True:
            event, values = self.gui.window.read(timeout=1000)

            if event in [sg.WINDOW_CLOSED, 'main_exit_btn']:
                break

            elif event == 'main_newgame_btn':
                self.make_screen_visible('main_screen', 'new_game_screen')

            elif event == 'main_loadgame_btn':
                self.make_screen_visible('main_screen', 'load_game_screen')

            elif event == 'debug_cancelmain_btn':
                self.make_screen_visible('debug_game_mode_screen', 'main_screen')

            elif event == 'debug_cancel_btn':
                if self.is_match_running:
                    self.controller.current_match.is_match_over = True
                self.make_screen_visible('debug_match_screen', 'main_screen')

            elif event == 'main_debug_btn':
                self.make_screen_visible('main_screen', 'debug_game_mode_screen')

            elif event == 'main_newgame_btn':
                self.make_screen_visible('main_screen', 'new_game_screen')

            elif event == 'main_loadgame_btn':
                self.make_screen_visible('main_screen', 'load_game_screen')

            elif event == 'main_settings_btn':
                self.make_screen_visible('main_screen', 'settings_screen')

            elif event == 'load_game_cancel_btn':
                self.make_screen_visible('load_game_screen', 'main_screen')

            elif event == 'ng_cancel_btn':
                self.make_screen_visible('new_game_screen', 'main_screen')

            elif event == 'settings_cancel_btn':
                self.make_screen_visible('settings_screen', 'main_screen')

            elif event == 'debug_pickteam_btn':
                self.make_screen_visible('debug_game_mode_screen', 'debug_pickteam_screen')

            elif event == 'debug_match_btn':
                self.controller.check_files()
                if not self.controller.current_match:
                    match_live = self.controller.initialize_random_debug_match()
                else:
                    match_live = self.controller.current_match

                data = self.team_data(match_live=match_live)
                self.gui.update_debug_match_info(match_live, data)
                self.make_screen_visible('debug_game_mode_screen', 'debug_match_screen')

            elif event == 'settings_generate_btn':
                try:
                    value = int(values['settings_amount_input'])
                except ValueError:
                    self.controller.amount_players = 400
                    self.gui.window['settings_amount_input'].update(value=400)
                else:
                    self.controller.amount_players = value
                self.controller.generate_all_data()

            elif event == 'debug_startmatch_btn':
                self.is_match_running = True
                self.controller.reset_match(match_live)
                self.controller.current_match.is_match_over = False
                self.controller.start_match_sim_thread()

            elif event == 'debug_newteams_btn':
                self.controller.check_files()
                match_live = self.controller.initialize_random_debug_match()
                data = self.team_data(match_live=match_live)
                self.gui.update_debug_match_info(match_live, data)

            elif event == 'debug_resetmatch_btn':
                self.controller.reset_match(match_live)
                data = self.team_data(match_live=match_live)
                self.gui.update_debug_match_info(match_live, data)

            if match_live is not None:
                if values['debug_simulate_checkbox']:
                    match_live.simulate = True
                else:
                    match_live.simulate = False

            if self.is_match_running:
                if not self.controller.current_match.is_match_over and self.controller.match_thread.is_alive():
                    data = self.team_data(self.controller.current_match)
                    self.gui.update_debug_match_info(self.controller.current_match, data)
                else:
                    self.is_match_running = False
