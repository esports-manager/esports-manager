import base64

import PySimpleGUI as sg

from src.core.match import Match
from src.core.pre_match import create_team_object, get_data
from src.resources import RES_DIR
from src.resources.generator.generate_players import get_players_nationalities
from src.resources.utils import find_file, load_list_from_json
from src.ui.gui_components import esm_button, esm_form_text, create_look_and_feel, \
    esm_input_text, esm_input_combo, esm_title_text, esm_listbox, esm_table, esm_calendar_button


def encode_icon() -> bytes:
    with open(find_file('esportsmanagertrophy.png', folder=RES_DIR), 'rb') as fp:
        encoded_icon = base64.b64encode(fp.read())

    return encoded_icon


def get_player_names(value: str, team_list: list, player_list: list) -> list:
    player_ids = None

    for team in team_list:
        if value[0] == team['id']:
            player_ids = team['roster_id']

    if player_ids is not None:
        player_names = []

        for pl_id in player_ids:
            for player in player_list:
                if pl_id == player['id']:
                    player_names.append([player['nick_name'],
                                         player['nationality'],
                                         player['skill']])
    else:
        raise NotImplementedError("Not found!")

    return player_names


def app() -> None:
    window = create_window()
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
            teams = load_list_from_json('teams.json')
            players = load_list_from_json('players.json')
            window.Element('player_list').Update(values=get_player_names(values['team_list'], teams, players))

        print(event, values)

    window.close()


def create_window() -> sg.Window:
    """
    Creates the main Window using PySimpleGUI, and assigns the eSM icon to it.
    It uses the get_layouts() function to get a list of layouts used in this software.
    :return: the window PySimpleGUI object
    """

    icon_path = encode_icon()
    create_look_and_feel()
    sg.theme('EsmTheme')
    return sg.Window(
        'eSports Manager',
        element_justification='center',
        layout=get_layouts(),
        # size=(900, 800),
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

    button_pad = (0, 15)
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
    nationalities = get_players_nationalities(load_list_from_json('names.json'))

    team_headings = ['Team #', 'Team Name', 'Skill']
    player_headings = ['Nickname', 'Nationality', 'Skill']

    data = get_data()

    team_list_frame = [
        [esm_form_text('Team: ')],
        [esm_table(data, key='team_list', headings=team_headings, enable_events=True)]
    ]
    player_list_frame = [
        [esm_form_text('Players: ')],
        [esm_table([['No team selected', ' ', ' ']], key='player_list', headings=player_headings)]
    ]

    return [
        [esm_title_text('New Game')],
        [esm_form_text('Manager Name: '),
         esm_input_text()],
        [esm_form_text('Date of Birth: ', ), esm_calendar_button(size=(20, 1))],
        [esm_form_text('Starting Season: '), esm_input_combo([i for i in range(2010, 2021)], key='-starting_season-')],
        [esm_form_text('Nationality: '), esm_input_combo(nationalities)],
        [sg.Column(layout=team_list_frame, element_justification='center'),
         sg.Column(layout=player_list_frame, element_justification='center')],
        [esm_button('Next', key='next_new_game'),
         esm_button('Cancel', key='cancel_new_game')]
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
def debug_window() -> sg.Window:
    icon_path = encode_icon()

    layout = get_debug_layout()

    create_look_and_feel()
    sg.theme('EsmTheme')
    return sg.Window(
        'eSports Manager',
        element_justification='center',
        layout=layout,
        icon=icon_path,
        resizable=True,
    )


def get_debug_layout(match: Match = None):
    return [
        [esm_form_text('Debug Match')],
        [esm_button('New Game')]
    ]

