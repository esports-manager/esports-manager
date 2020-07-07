import PySimpleGUI as sg

from src.ui.gui import create_window, match_test
from src.core.match_live import get_match_obj_test
from src.resources.generator.generate_champions import generate_champion_file
from src.resources.generator.generate_teams import generate_team_file
from src.resources.generator.generate_players import generate_player_file


def generation():
    generate_champion_file()
    generate_player_file()
    generate_team_file()


def testing_match():
    match = get_match_obj_test()
    window = match_test(match)
    while True:
        event, values = window.read()
        if event in [sg.WINDOW_CLOSED, 'exit_main']:
            break

    window.close()


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
        print(event, values)

    window.close()


if __name__ == '__main__':
    app()
