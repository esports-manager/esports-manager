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

import base64
import PySimpleGUI as sg

from src.core.esports.moba.match_live import MatchLive
from src.resources import RES_DIR
from src.resources.utils import find_file
from src.ui.gui_components import *


class View:
    def __init__(self, controller):
        self.gui = GUI(controller)
        self.controller = controller
        self.is_match_running = False
    
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
            
            elif event == 'debug_cancel_btn':
                if self.is_match_running:
                    self.controller.current_match.is_match_over = True
                self.make_screen_visible('debug_screen', 'main_screen')
            
            elif event == 'main_debug_btn':
                self.controller.check_files()
                if not self.controller.current_match:
                    match_live = self.controller.initialize_debug_match()
                else:
                    match_live = self.controller.current_match
                
                data = self.team_data(match_live=match_live)
                self.gui.update_debug_match_info(match_live, data)
                self.make_screen_visible('main_screen', 'debug_screen')
            
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
            
            elif event == 'debug_startmatch_btn':
                self.is_match_running = True
                self.controller.reset_match(match_live)
                self.controller.current_match.is_match_over = False
                self.controller.start_match_sim_thread()
            
            elif event == 'debug_newteams_btn':
                self.controller.check_files()
                match_live = self.controller.initialize_debug_match()
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
            

class GUI:
    def __init__(self, controller):
        create_look_and_feel()
        self.icon = 'esportsmanagertrophy.png'
        self.window = self._create_window()
        self.layouts = None
        self.controller = controller

    def _encode_icon(self) -> bytes:
        with open(find_file(self.icon, folder=RES_DIR), 'rb') as fp:
            encoded_icon = base64.b64encode(fp.read())

        return encoded_icon

    def _create_window(self, theme='EsmTheme') -> sg.Window:
        """
        Creates the main Window using PySimpleGUI, and assigns the eSM icon to it.
        It uses the _get_layouts() function to get a list of layouts used in this software.
        :return: the window PySimpleGUI object
        """

        encoded_icon = self._encode_icon()
        
        sg.theme(theme)
        self.layouts = self._get_layouts()
        return sg.Window(
            'eSports Manager',
            element_justification='center',
            layout=self.layouts,
            size=(1300, 780),
            icon=encoded_icon,
            resizable=True,
        )

    def _get_layouts(self) -> list:
        """
        Gets all the layouts and makes them all invisible, except for the main screen one.
        This function gets called in the beginning of the game's execution.
        :return:
        """
        col_main_screen = sg.Column(self.main_screen(),
                                    key='main_screen',
                                    element_justification="center"
                                    )

        col_main_debug = sg.Column(self.debug_layout(),
                                    key='debug_screen',
                                    visible=False,
                                    element_justification="center"
                                    )
        
        col_newgame_screen = sg.Column(self.new_game_layout(),
                                        key='new_game_screen',
                                        visible=False,
                                        element_justification="center"
                                        )
        
        col_loadgame_screen = sg.Column(self.load_game_layout(),
                                        key='load_game_screen',
                                        visible=False,
                                        element_justification="center"
                                        )
        
        col_settings_screen = sg.Column(self.settings_layout(),
                                        key='settings_screen',
                                        visible=False,
                                        element_justification="center"
                                        )
        

        return [
            [sg.Pane([col_main_screen,
                      col_main_debug,
                      col_newgame_screen,
                      col_loadgame_screen,
                      col_settings_screen,
                    ],
                     relief=sg.RELIEF_FLAT, show_handle=False
                    )]
        ]

    def main_screen(self) -> list:
        """
        Defines the main screen. This screen shows the initial options to play a new game, load game,
        use the Database Editor, or exit the game.
        """
        logo_path = find_file('esportsmanager.png')

        button_pad = (0, 10)
        button_size = (20, 2)

        return [
            [sg.Image(logo_path, pad=(50,0))],
            [esm_button('Debug Game Mode',
                        key ='main_debug_btn',
                        pad=button_pad,
                        size=button_size
            )],
            [esm_button('New Game',
                        key ='main_newgame_btn',
                        pad=button_pad,
                        size=button_size
            )],
            [esm_button('Load Game',
                        key ='main_loadgame_btn',
                        pad=button_pad,
                        size=button_size
            )],
            [esm_button('Settings',
                        key ='main_settings_btn',
                        pad=button_pad,
                        size=button_size
            )],
            [esm_button('Exit',
                        key ='main_exit_btn',
                        pad=button_pad,
                        size=button_size
            )],
        ]

    def update_debug_match_info(self, match, data):
        window = self.window
        window.Element('debug_team1table').update(values=data[0])
        window.Element('debug_team2table').update(values=data[1])
        window.Element('debug_team1skill').update(value=match.match.team1.total_skill)
        window.Element('debug_team2skill').update(value=match.match.team2.total_skill)
        window.Element('debug_team1winprob').Update(value=match.match.team1.win_prob)
        window.Element('debug_team2winprob').Update(value=match.match.team2.win_prob)
        window.Element('debug_team1towers').Update(value=match.match.team1.towers)
        window.Element('debug_team2towers').Update(value=match.match.team2.towers)
        window.Element('debug_team1inhibs').Update(value=match.match.team1.inhibitors)
        window.Element('debug_team2inhibs').Update(value=match.match.team2.inhibitors)
        window.Element('debug_team1name').Update(value=match.match.team1.name)
        window.Element('debug_team2name').Update(value=match.match.team2.name)
        window.refresh()

    def new_game_layout(self) -> list:
        """
        Defines the new game screen.
        """

        label_pad = (0, 5)
        size_element = (29,1)

        labels = [
            [esm_form_text('Game Name:', pad=label_pad)],
        ]

        inputs = [
            [esm_input_text(key='ng_gamename_input', size=size_element)]
        ]

        return [
            [esm_title_text('New Game')],
            [sg.Column(labels, element_justification='left'), sg.Column(inputs, element_justification='left')],
            [esm_button('Create Game', key='ng_creategame_btn'), esm_button('Cancel', key='ng_cancel_btn')]
        ]

    def load_game_layout(self):
        saved_games = [
            'Saved Game 1',
            'Saved Game 2',
            'Saved Game 3',
        ]

        size_btn = (10,1)

        return [
            [esm_title_text('Load Game')],
            [esm_form_text('Saved Games:')],
            [esm_listbox(saved_games, size=(50, 20), key='load_game_listbox', enable_events=True)],
            [esm_button('Load Game', key='load_game_btn', size=size_btn),
            esm_button('Cancel', key='load_game_cancel_btn', size=size_btn)]
        ]
    
    def settings_layout(self):
        size_elements = (45, 2)
        
        languages = ['English', 'Portuguese']

        ch_file = find_file('champions.json')
        pl_file = find_file('players.json')
        t_file = find_file('teams.json')

        labels = [
            [esm_form_text('Language:')],
            [esm_form_text('Font scale:')],
            [esm_form_text('Champions file:')],
            [esm_form_text('Players file:')],
            [esm_form_text('Teams file:')],
        ]

        controls = [
            # TODO: Replace with supported i18n
            [esm_input_combo(languages, default_value=languages[0], size=size_elements, key='settings_languages_inpcombo')],
            [esm_input_text('1', size=size_elements, key='settings_fontsize_input')],
            [esm_input_text(ch_file, size=size_elements, key='settings_ch_file'),
            sg.FileBrowse(target='settings_ch_file')],
            [esm_input_text(pl_file, size=size_elements, key='settings_pl_file'),
            sg.FileBrowse(target='settings_pl_file')],
            [esm_input_text(t_file, size=size_elements, key='settings_t_file'),
            sg.FileBrowse(target='settings_t_file')],
        ]
        
        return [
            [esm_title_text('Settings')],
            [sg.Column(labels, element_justification='left'),
            sg.Column(controls, element_justification='left')],
            [esm_button('Apply', key='settings_apply_btn'),
            esm_button('Cancel', key='settings_cancel_btn')]
        ]

    def debug_layout(self):
        headings = ['Lane', 'Player Name', 'Kills', 'Deaths', 'Assists', 'Champion', 'Skill']

        team1_column = [
            [esm_form_text('Team1DebugMatch', key='debug_team1name'),
            esm_form_text('0000', key='debug_team1skill')],
            [esm_form_text('0.0000', key='debug_team1winprob')],
            [esm_table(headings, headings=headings, key='debug_team1table')],
            [esm_form_text({
                        "top": 3,
                        "mid": 3,
                        "bot": 3,
                        "base": 2
                    }, key='debug_team1towers')],
            [esm_form_text({
                        "top": 1,
                        "mid": 1,
                        "bot": 1
                    }, key='debug_team1inhibs')]
        ]

        
        team2_column = [
            [esm_form_text('Team2DebugMatch', key='debug_team2name'),
            esm_form_text('0000', key='debug_team2skill')],
            [esm_form_text('0.0000', key='debug_team2winprob')],
            [esm_table(headings, headings=headings, key='debug_team2table')],
            [esm_form_text({
                        "top": 3,
                        "mid": 3,
                        "bot": 3,
                        "base": 2
                    }, key='debug_team2towers')],
            [esm_form_text({
                        "top": 1,
                        "mid": 1,
                        "bot": 1
                    }, key='debug_team2inhibs')]
        ]

        return [
            [esm_title_text('Debug Match')],
            [sg.Column(layout=team1_column, element_justification='center'),
            sg.Column(layout=team2_column, element_justification='center')],
            [esm_output()],
            [esm_checkbox('Simulate step-by-step', key='debug_simulate_checkbox')],
            [esm_button('Start Match', key='debug_startmatch_btn'),
            esm_button('New Teams', key='debug_newteams_btn'),
            esm_button('Reset Match', key='debug_resetmatch_btn'),
            esm_button('Cancel', key='debug_cancel_btn')]
        ]
        


