import PySimpleGUI as sg

from src.ui.gui import app, debug_window
from src.resources.generator.generate_champions import generate_champion_file
from src.resources.generator.generate_teams import generate_team_file
from src.resources.generator.generate_players import generate_player_file


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


if __name__ == '__main__':
    generation()
    app()
