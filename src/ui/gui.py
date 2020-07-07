import PySimpleGUI as sg

from src.ui.gui_components import esm_button, esm_form_text, create_look_and_feel, \
                                  esm_input_text, esm_input_combo, esm_title_text, esm_listbox
from src.resources.generator.generate_players import get_players_nationalities
from src.resources.utils import get_list_of_team_names, find_file
from src.core.match import Match


def create_window() -> sg.Window:
    """
    Creates the main Window using PySimpleGUI, and assigns the eSM icon to it.
    It uses the get_layouts() function to get a list of layouts used in this software.
    :return: the window PySimpleGUI object
    """
    icon_path = find_file('esportsmanagertrophy.png')

    create_look_and_feel()
    sg.theme('EsmTheme')
    return sg.Window(
        'eSports Manager',
        element_justification='center',
        layout=get_layouts(),
        icon=icon_path,
        resizable=True,
    )


def main_screen() -> list:
    """
    Defines the main screen. This screen shows the initial options to play a new game, load game,
    use the Database Editor, or exit the game.
    :return: layout of the main screen
    """
    logo_path = find_file('esportsmanager.png')

    button_pad = (300, 15)
    button_size = (20, 1)

    return [
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


def create_manager_layout() -> list:
    """
    Defines the manager creation layout. In this page, the user chooses a name for the manager, the team they
    want to play with, and
    :return:
    """
    nationalities = get_players_nationalities()
    team_names = get_list_of_team_names()

    return [
        [esm_title_text('New Game')],
        [esm_form_text('Manager Name: '),
         esm_input_text()],
        [esm_form_text('Date of Birth: '), esm_input_text()],
        [esm_form_text('Nationality: '), esm_input_combo(nationalities)],
        [esm_form_text('Team: '), esm_listbox(team_names)],
        [esm_button('Next', key='next_new_game', font='Yukarimobile 18'),
         esm_button('Cancel', key='cancel_new_game', font='Yukarimobile 18')]
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
        [esm_listbox(saved_games)],
        [esm_button('Load Game', key='load_game_btn'),
         esm_button('Cancel', key='cancel_load')]
    ]


def get_layouts() -> list:
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


# debugging
def match_test(match: Match) -> sg.Window:
    icon_path = find_file('esportsmanagertrophy.png')
    match_name = 'Match ' + str(match.match_id)

    layout = [
        [esm_title_text(match_name)]
    ]

    create_look_and_feel()
    sg.theme('EsmTheme')
    return sg.Window(
        'eSports Manager',
        element_justification='center',
        layout=layout,
        icon=icon_path,
        resizable=True,
    )
