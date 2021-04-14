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

import base64

import PySimpleGUI as sg

from src.core.esports.moba.match_live import MatchLive
from src.resources import RES_DIR
from src.resources.utils import find_file
from src.ui.gui_components import *


class GUI:
    def __init__(self, controller):
        self.controller = controller
        self.icon = 'esportsmanagertrophy.png'
        self.layouts = self._get_layouts()
        self.window = self._create_window()

    def _encode_icon(self) -> bytes:
        with open(find_file(self.icon, folder=RES_DIR), 'rb') as fp:
            encoded_icon = base64.b64encode(fp.read())

        return encoded_icon

    def _create_window(self) -> sg.Window:
        """
        Creates the main Window using PySimpleGUI, and assigns the eSM icon to it.
        It uses the get_layouts() function to get a list of layouts used in this software.
        :return: the window PySimpleGUI object
        """

        encoded_icon = self._encode_icon()
        create_look_and_feel()
        sg.theme('EsmTheme')
        return sg.Window(
            'eSports Manager',
            element_justification='center',
            layout=self.layouts,
            # size=(900, 800),
            icon=encoded_icon,
            resizable=True,
        )

    def _get_layouts(self) -> list:
        """
        Gets all the layouts and makes them all invisible, except for the main screen one.
        This function gets called in the beginning of the game's execution.
        :return:
        """
        col_main_screen = sg.Column(main_screen(),
                                    key='main_screen',
                                    element_justification="center"
                                    )

        col_create_manager = sg.Column(create_manager_layout(),
                                       key='create_manager',
                                       visible=False,
                                       element_justification="center"
                                       )

        col_load_game = sg.Column(load_game_layout(),
                                  key='load_game',
                                  visible=False,
                                  element_justification="center"
                                  )

        return [
            [sg.Pane([col_main_screen,
                      col_create_manager,
                      col_load_game],
                     relief=sg.RELIEF_FLAT, show_handle=False)]
        ]


def get_player_names(value: str, teams) -> list:
    for team in teams:
        if value[0] == team.team_id:
            return [[player.get_lane(),
                     player.nick_name,
                     player.nationality,
                     int(player.skill * player.get_highest_multiplier())] for player in team.list_players]

    else:
        raise NotImplementedError("Not found!")


def app() -> None:
    window = create_window()
    v = [0]
    teams = get_all_team_objects()
    while True:
        event, values = window.read()
        if event in [sg.WINDOW_CLOSED, 'exit_main']:
            break
        elif event == 'new_game':
            window['main_screen'].update(visible=False)
            window['create_manager'].update(visible=True)
        elif event == 'load_game_main':
            window['main_screen'].update(visible=False)
            window['load_game'].update(visible=True)
        elif event == 'cancel_load':
            window['load_game'].update(visible=False)
            window['main_screen'].update(visible=True)
        elif event == 'cancel_new_game':
            window['create_manager'].update(visible=False)
            window['main_screen'].update(visible=True)
        elif event == 'team_list':
            value = values['team_list']
            v = window.Element('team_list').Values[value[0]]
            window.Element('player_list').Update(values=get_player_names(v, teams))

        print(event, values)
        print(v[0])

    window.close()


def main_screen() -> list:
    """
    Defines the main screen. This screen shows the initial options to play a new game, load game,
    use the Database Editor, or exit the game.
    :return: layout of the main screen
    """
    logo_path = find_file('esportsmanager.png')

    button_pad = (0, 10)
    button_size = (20, 2)

    return [
        [sg.Image(logo_path, pad=(50, 0))],
        [esm_button('New Game',
                    key='new_game',
                    pad=button_pad,
                    size=button_size
                    )],
        [esm_button('Load Game',
                    key='load_game_main',
                    pad=button_pad,
                    size=button_size
                    )],
        [esm_button('Settings',
                    key='settings',
                    pad=button_pad,
                    size=button_size
                    )],
        # TODO: implement editor
        # [esm_button('Editor',
        #             key='editor_main',
        #             pad=button_pad,
        #             size=button_size
        #             )],
        [esm_button('Exit',
                    key='exit_main',
                    pad=button_pad,
                    size=button_size
                    )]
    ]


def create_manager_layout() -> list:
    """
    Defines the manager creation layout. In this page, the user chooses a name for the manager, the team they
    want to play with, and
    :return:
    """
    nationalities = ['Brazil', 'United States', 'Korea']

    team_headings = ['Team #', 'Team Name', 'Skill']
    player_headings = ['Lane', 'Nickname', 'Nationality', 'Skill']

    data = get_data()

    labels = [
        [esm_form_text('First Name: ', pad=(0, 5))],
        [esm_form_text('Last Name: ', pad=(0, 5))],
        [esm_form_text('Nick Name: ', pad=(0, 5))],
        [esm_form_text('Nationality: ', pad=(0, 5))],
        [esm_form_text('Date of Birth: ', pad=(0, 5))]
    ]

    controls = [
        [esm_input_text(key='-First Name-')],
        [esm_input_text(key='-Last Name-')],
        [esm_input_text(key='-Nick Name-')],
        [esm_input_combo(nationalities, key='-Manager Nat-', size=(29, 1))],
        [esm_calendar_button(button_text='Select date', size=(20, 1), key='-DOB-', enable_events=True)],
    ]

    team_list_frame = [
        [esm_form_text('Team: ')],
        [esm_table(data, key='team_list', headings=team_headings, enable_events=True)]
    ]
    player_list_frame = [
        [esm_form_text('Players: ')],
        [esm_table([[' ', 'Select team', ' ', ' ']], key='player_list', headings=player_headings)]
    ]

    return [
        [esm_title_text('New Game')],
        # TODO: we have to create a check on events to check if the input text fields are larger than 20 characters to
        # avoid abuses
        [sg.Column(layout=labels, element_justification='left'),
         sg.Column(layout=controls, element_justification='left')],
        # TODO: implement starting season, putting this on hold for 0.1.0-alpha, maybe 0.2.0 should include it?
        # [esm_form_text('Starting Season: '), esm_input_combo([i for i in range(2010, 2021)], key='-Starting Season-')]
        [sg.Column(layout=team_list_frame, element_justification='center'),
         sg.Column(layout=player_list_frame, element_justification='center')],
        [esm_button('Cancel', key='cancel_new_game', size=(10, 1)),
         esm_button('Next', key='next_new_game', size=(10, 1))]
    ]


def load_game_layout() -> list:
    """
    Creates the layout for the load game page
    :return:
    """
    saved_games = [
        'Saved Game 1',
        'Saved Game 2',
        'Saved Game 3'
    ]

    return [
        [esm_title_text('Load Game')],
        [esm_form_text('Saved Games: ')],
        [esm_listbox(saved_games, size=(50, 20), enable_events=True)],
        [esm_button('Cancel', key='cancel_load', size=(10, 1)),
         esm_button('Load Game', key='load_game_btn', size=(10, 1))]
    ]

# debugging
def debug_window(match) -> sg.Window:
    icon_path = encode_icon()

    create_look_and_feel()
    sg.theme('EsmTheme')

    layout1 = sg.Column(get_debug_layout(match), visible=False, element_justification='center')
    layout2 = sg.Column(picks_and_bans_layout(match), visible=True, element_justification='center')

    layout = [[sg.Pane([layout1, layout2], relief=sg.RELIEF_FLAT, show_handle=False)]]

    return sg.Window(
        'eSports Manager',
        element_justification='center',
        layout=layout,
        icon=icon_path,
        resizable=True,
    )


def get_team_data(match: MatchLive = None):
    players = [[player for player in team.list_players] for team in match.match.teams]

    # The event handler shuffles players, let's keep their order straight up
    for team in players:
        team.sort(key=lambda x: x.lane.value)

    data = []
    for team in players:
        team_data = [[player.lane.name,
                      player.nick_name,
                      player.kills,
                      player.deaths,
                      player.assists,
                      player.champion,
                      int(player.get_player_total_skill())] for player in team]
        data.append(team_data)

    return data


def get_debug_layout(match: MatchLive = None):
    data = get_team_data(match)

    headings = ['Lane', 'Player Name', 'Kills', 'Deaths', 'Assists', 'Champion', 'Skill']

    team1_column = [
        [esm_form_text(match.match.team1.name, key='team1name'),
         esm_form_text(text=match.match.team1.total_skill, key='team1skill')],
        [esm_form_text(match.match.team1.win_prob, key='team1winprob')],
        [esm_table(data[0], headings=headings, key='-Team1Table-')],
        [esm_form_text(match.match.team1.towers, key='team1towers')],
        [esm_form_text(match.match.team1.inhibitors, key='team1inhibs')]
    ]

    team2_column = [
        [esm_form_text(match.match.team2.name, key='team2name'),
         esm_form_text(text=match.match.team2.total_skill, key='team2skill')],
        [esm_form_text(match.match.team2.win_prob, key='team2winprob')],
        [esm_table(data[1], headings=headings, key='-Team2Table-')],
        [esm_form_text(match.match.team2.towers, key='team2towers')],
        [esm_form_text(match.match.team2.inhibitors, key='team2inhibs')]
    ]

    return [
        [esm_title_text('Debug Match')],
        [sg.Column(layout=team1_column, element_justification='center'),
         sg.Column(layout=team2_column, element_justification='center')],
        [esm_output()],
        [esm_button('Start Match', key='-StartMatch-'), esm_button('New Teams', key='-NewTeams-')]
    ]


def picks_and_bans_layout(match: MatchLive = None):
    players = [[player for player in team.list_players] for team in match.match.teams]

    data = []
    for team in players:
        team_data = [[player.lane.name,
                      player.nick_name,
                      int(player.get_player_total_skill()),
                      player.champion,
                      ] for player in team]
        data.append(team_data)

    champions_names = [champion.name for champion in match.champions.champions_obj]

    headings = ['Lane', 'Player', 'Skill', 'Champion']

    team1_column = [
        [esm_form_text(match.match.team1.name, key='team1namepicks')],
        [esm_table(data[0], headings=headings, key='-Team1PicksBans')]
    ]

    team2_column = [
        [esm_form_text(match.match.team2.name, key='team2namepicks')],
        [esm_table(data[1], headings=headings, key='-Team2PicksBans')]
    ]

    champion_column = [
        [esm_listbox(champions_names, key='champions_pick_ban')]
    ]

    return [
        [esm_title_text('Debug Picks Bans')],
        [sg.Column(layout=team1_column, element_justification='center'),
         sg.Column(layout=champion_column, element_justification='center'),
         sg.Column(layout=team2_column, element_justification='center')],
        [esm_button('Pick', key='Pick')]
    ]
