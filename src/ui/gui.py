import os
import PySimpleGUI as sg

from src.ui.gui_components import esm_button, esm_form_text, create_look_and_feel, \
                                  esm_input_text, esm_input_combo, esm_title_text, esm_listbox
from src.resources.generator.generate_players import get_players_nationalities
from src.resources.utils import get_list_of_team_names

folder = os.path.dirname(os.path.abspath(__file__))


def create_window():
    """
    Creates the main Window using PySimpleGUI, and assigns the eSM icon to it.
    It uses the get_layouts() function to get a list of layouts used in this software.
    :return: the window PySimpleGUI object
    """
    icon_path = os.path.join(folder, '../resources/images/logo/esportsmanagertrophy.png')

    create_look_and_feel()
    sg.theme('EsmTheme')
    window = sg.Window('eSports Manager', element_justification='center', layout=get_layouts(), icon=icon_path, resizable=True)

    return window


def main_screen():
    """
    Defines the main screen. This screen shows the initial options to play a new game, load game,
    use the Database Editor, or exit the game.
    :return: layout of the main screen
    """
    logo_path = os.path.join(folder, '../resources/images/logo/esportsmanager.png')

    button_pad = (300, 15)
    button_size = (20, 1)

    layout = [
        [sg.Image(logo_path, pad=(100, 0))],
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
        [esm_button('Editor',
                    key='editor_main',
                    pad=button_pad,
                    size=button_size
                    )],
        [esm_button('Exit',
                    key='exit_main',
                    pad=button_pad,
                    size=button_size
                    )]
    ]

    return layout


def create_manager_layout():
    """
    Defines the manager creation layout. In this page, the user chooses a name for the manager, the team they
    want to play with, and
    :return:
    """
    nationalities = get_players_nationalities()
    team_names = get_list_of_team_names()

    layout = [
        [esm_title_text('New Game')],
        [esm_form_text('Manager Name: '),
         esm_input_text()],
        [esm_form_text('Date of Birth: '), esm_input_text()],
        [esm_form_text('Nationality: '), esm_input_combo(nationalities)],
        [esm_form_text('Team: '), esm_listbox(team_names)],
        [esm_button('Next', font='Yukarimobile 18'),
         esm_button('Cancel', font='Yukarimobile 18')]
    ]

    return layout


def load_game_layout():
    """
    Creates the layout for the load game page
    :return:
    """
    saved_games = [
        'Saved Game 1',
        'Saved Game 2',
        'Saved Game 3'
    ]

    layout = [
        [esm_title_text('Load Game')],
        [esm_form_text('Saved Games: ')],
        [esm_listbox(saved_games)],
        [esm_button('Load Game', key='load_game_btn'),
         esm_button('Cancel', key='cancel_load')]
    ]

    return layout


def get_layouts():
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

    layout = [
        [sg.Pane([col_main_screen,
                  col_create_manager,
                  col_load_game],
                 relief=sg.RELIEF_FLAT, show_handle=False)]
    ]

    return layout
