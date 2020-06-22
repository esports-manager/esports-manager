import PySimpleGUI as sg

from src.ui.gui import create_window


def app():
    window = create_window()
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'exit_main':
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
        print(event, values)

    window.close()


if __name__ == '__main__':
    app()
