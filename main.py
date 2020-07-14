import PySimpleGUI as sg

from src.ui.gui import create_window, debug_window
from src.core.match_live import get_match_obj_test
from src.resources.generator.generate_champions import generate_champion_file
from src.resources.generator.generate_teams import generate_team_file
from src.resources.generator.generate_players import generate_player_file
from src.resources.utils import load_list_from_json, get_key_from_json


def generation():
    generate_champion_file()
    generate_player_file()
    generate_team_file()


def testing_match():
    window = debug_window()
    while True:
        event, values = window.read()
        if event in [sg.WINDOW_CLOSED, 'exit_main']:
            break

    window.close()


def get_player_names(value: str, team_list: list, player_list: list) -> list:
    player_ids = None
    for team in team_list:
        if value[0] == team['name']:
            player_ids = team['roster_id']

    if player_ids is not None:
        player_names = []

        for pl_id in player_ids:
            for player in player_list:
                if pl_id == player['id']:
                    player_names.append(player['nick_name'])
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


if __name__ == '__main__':
    import time
    start_time = time.time()
    generation()
    print(time.time() - start_time)
    app()
