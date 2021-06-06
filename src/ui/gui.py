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
import traceback

from src.core.esports.moba.match_live import MatchLive
from src.resources import RES_DIR
from src.resources.utils import find_file
from src.ui.gui_components import *


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

        col_debug_match_screen = sg.Column(self.debug_layout(),
                                           key='debug_match_screen',
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

        col_debug_gamemode_screen = sg.Column(self.debug_game_mode_screen(),
                                              key='debug_game_mode_screen',
                                              visible=False,
                                              element_justification="center"
                                              )

        col_debug_pickteam_screen = sg.Column(self.debug_pick_a_team(),
                                              key='debug_pickteam_screen',
                                              visible=False,
                                              element_justification="center"
                                              )

        col_debug_picks_bans_screen = sg.Column(self.debug_picks_bans(),
                                                key='debug_picks_bans_screen',
                                                visible=False,
                                                element_justification="center"
                                                )

        return [
            [sg.Pane([col_main_screen,
                      col_newgame_screen,
                      col_loadgame_screen,
                      col_settings_screen,
                      col_debug_gamemode_screen,
                      col_debug_match_screen,
                      col_debug_pickteam_screen,
                      col_debug_picks_bans_screen,
                      ],
                     relief=sg.RELIEF_FLAT, show_handle=False
                     )]
        ]

    @staticmethod
    def generate_data_window(players, teams, champions):
        for i, _ in enumerate(champions):
            sg.one_line_progress_meter('Generating Champions', i + 1, len(champions), 'generate_champ')

        for i, _ in enumerate(players):
            sg.one_line_progress_meter('Generating players', i + 1, len(players), 'generate_players')

        for i, _ in enumerate(teams):
            sg.one_line_progress_meter('Generating teams', i + 1, len(teams), 'generate_teams')

    @staticmethod
    def main_screen() -> list:
        """
        Defines the main screen. This screen shows the initial options to play a new game, load game,
        use the Database Editor, or exit the game.
        """
        logo_path = find_file('esportsmanager.png')

        button_pad = (0, 10)
        button_size = (20, 2)

        return [
            [sg.Image(logo_path, pad=(50, 0))],
            [esm_button('Debug Game Mode',
                        key='main_debug_btn',
                        pad=button_pad,
                        size=button_size
                        )],
            [esm_button('New Game',
                        key='main_newgame_btn',
                        pad=button_pad,
                        size=button_size
                        )],
            [esm_button('Load Game',
                        key='main_loadgame_btn',
                        pad=button_pad,
                        size=button_size
                        )],
            [esm_button('Settings',
                        key='main_settings_btn',
                        pad=button_pad,
                        size=button_size
                        )],
            [esm_button('Exit',
                        key='main_exit_btn',
                        pad=button_pad,
                        size=button_size
                        )],
        ]

    def update_debug_match_info(self, match, data):
        win_prob = match.match.team1.win_prob * 100
        window = self.window
        window['debug_team1table'].update(values=data[0])
        window['debug_team2table'].update(values=data[1])
        window['debug_team1skill'].update(value=match.match.team1.total_skill)
        window['debug_team2skill'].update(value=match.match.team2.total_skill)
        window['debug_team1winprob'].update(value=match.match.team1.win_prob)
        window['debug_team2winprob'].update(value=match.match.team2.win_prob)
        window['debug_winprob'].update_bar(win_prob)
        window['debug_team1towers'].Update(value=match.match.team1.towers)
        window['debug_team2towers'].Update(value=match.match.team2.towers)
        window['debug_team1inhibs'].Update(value=match.match.team1.inhibitors)
        window['debug_team2inhibs'].Update(value=match.match.team2.inhibitors)
        window['debug_team1name'].Update(value=match.match.team1.name)
        window['debug_team2name'].Update(value=match.match.team2.name)
        window.refresh()

    @staticmethod
    def new_game_layout() -> list:
        """
        Defines the new game screen.
        """

        label_pad = (0, 5)
        size_element = (29, 1)

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

    @staticmethod
    def load_game_layout():
        saved_games = [
            'Saved Game 1',
            'Saved Game 2',
            'Saved Game 3',
        ]

        size_btn = (10, 1)

        return [
            [esm_title_text('Load Game')],
            [esm_form_text('Saved Games:')],
            [esm_listbox(saved_games, size=(50, 20), key='load_game_listbox', enable_events=True)],
            [esm_button('Load Game', key='load_game_btn', size=size_btn),
             esm_button('Cancel', key='load_game_cancel_btn', size=size_btn)]
        ]

    @staticmethod
    def settings_layout():
        size_elements = (45, 2)

        languages = ['English', 'Portuguese']

        try:
            ch_file = find_file('champions.json')
            pl_file = find_file('players.json')
            t_file = find_file('teams.json')
        except FileNotFoundError:
            ch_file = 'champions.json'
            pl_file = 'players.json'
            t_file = 'teams.json'

        labels = [
            [esm_form_text('Language:')],
            [esm_form_text('Font scale:')],
            [esm_form_text('Champions file:')],
            [esm_form_text('Players file:')],
            [esm_form_text('Teams file:')],
            [esm_form_text('Generate new files:')]
        ]

        controls = [
            # TODO: Replace with supported i18n
            [esm_input_combo(languages, default_value=languages[0], size=size_elements,
                             key='settings_languages_inpcombo')],
            [esm_input_text('1', size=size_elements, key='settings_fontsize_input')],
            [esm_input_text(ch_file, size=size_elements, key='settings_ch_file'),
             sg.FileBrowse(target='settings_ch_file')],
            [esm_input_text(pl_file, size=size_elements, key='settings_pl_file'),
             sg.FileBrowse(target='settings_pl_file')],
            [esm_input_text(t_file, size=size_elements, key='settings_t_file'),
             sg.FileBrowse(target='settings_t_file')],
            [esm_input_text('400', key='settings_amount_input', size=size_elements),
             esm_button('Generate', font=(default_font, default_font_size), key='settings_generate_btn')]
        ]

        return [
            [esm_title_text('Settings')],
            [sg.Column(labels, element_justification='right'),
             sg.Column(controls, element_justification='left')],
            [esm_button('Apply', key='settings_apply_btn'),
             esm_button('Cancel', key='settings_cancel_btn')]
        ]

    @staticmethod
    def debug_game_mode_screen() -> list:
        """
        Defines the Debug Game Mode screen. This screen shows the Debug game options.
        """

        button_pad = (0, 10)
        button_size = (20, 2)

        return [
            [esm_title_text('Choose your debug mode')],
            [esm_button('Debug Match',
                        key='debug_match_btn',
                        pad=button_pad,
                        size=button_size
                        )],
            [esm_button('Debug Pick Team',
                        key='debug_pickteam_btn',
                        pad=button_pad,
                        size=button_size
                        )],
            [esm_button('Debug Picks Bans',
                        key='debug_picksbans_btn',
                        pad=button_pad,
                        size=button_size
                        )],
            [esm_button('Cancel',
                        key='debug_cancelmain_btn',
                        pad=button_pad,
                        size=button_size
                        )],
            [esm_button('Exit',
                        key='main_exit_btn',
                        pad=button_pad,
                        size=button_size
                        )],
        ]

    @staticmethod
    def debug_pick_a_team():

        team_headings = ['Team Name', 'Skill']
        player_headings = ['Lane', 'Nickname', 'Nationality', 'Skill']

        team_list_frame = [
            [esm_form_text('Team:')],
            [esm_table(values=[['', '']], key='debug_pick_team_table', headings=team_headings, enable_events=True)]
        ]

        player_list_frame = [
            [esm_form_text('Players:')],
            [esm_table(values=[['', 'Select a team', '', '']], key='debug_pick_player_table', headings=player_headings,
                       enable_events=True)]
        ]

        return [
            [esm_title_text('Pick your team')],
            [sg.Column(team_list_frame, element_justification='center'),
             sg.Column(player_list_frame, element_justification='center')],
            [esm_button('Confirm', key='debug_confirmteam_btn'),
             esm_button('Cancel', key='debug_cancelteam_btn')]
        ]

    @staticmethod
    def debug_picks_bans():
        team_headings = ['Lane', 'Nickname', 'Skill', 'Champion', 'Ch. Skill']

        champion_headings = ['Name', 'Skill', 'Status']

        col_team1 = [
            [esm_form_text('Team1WholeName')],
            [esm_table(values=[['PLAYERLANE', 'PLAYERNICKNAME', 'PLAYERSKILLLEVEL', 'PLAYERCHAMPIONNAME', 'PLAYERCHAMPIONSKILLLEVEL']], headings=team_headings, key='pickban_team1_table', num_rows=5)]
        ]

        col_team2 = [
            [esm_form_text('Team2WholeName')],
            [esm_table(values=[['PLAYERLANE', 'PLAYERNICKNAME', 'PLAYERSKILLLEVEL', 'PLAYERCHAMPIONNAME', 'PLAYERCHAMPIONSKILLLEVEL']], headings=team_headings, key='pickban_team2_table', num_rows=5)]
        ]

        col_champion = [
            [esm_form_text('Champions')],
            [esm_table(values=[['CHAMPIONWHOLENAME', 'CHAMPIONSKILLLV', 'CHAMPIONSTATUS']], headings=champion_headings, key='pickban_champion_table', num_rows=10)]
        ]

        return [
            [esm_title_text('Picks and Bans')],
            [sg.Column(col_team1)],
            [sg.Column(col_champion)],
            [sg.Column(col_team2)],
            [esm_button('Pick', key='pickban_pick_btn'), esm_button('Cancel', key='pickban_cancel_btn')]
        ]

    @staticmethod
    def debug_layout():
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
            [sg.ProgressBar(100, size=(80, 20), border_width=1, key='debug_winprob')],
            [esm_output()],
            [esm_checkbox('Simulate step-by-step', key='debug_simulate_checkbox')],
            [esm_button('Start Match', key='debug_startmatch_btn'),
             esm_button('New Teams', key='debug_newteams_btn'),
             esm_button('Reset Match', key='debug_resetmatch_btn'),
             esm_button('Cancel', key='debug_cancel_btn')]
        ]

    @staticmethod
    def error_message(e):
        tb = traceback.format_exc()
        sg.Print('The following error happened:', e, tb)
        sg.popup_error(f'The following error occurred:', e, tb)
