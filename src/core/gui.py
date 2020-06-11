import os
import PySimpleGUI as sg
import base64


from src.core.match_live import get_match_info, get_match_obj


def new_game():
    folder = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(folder, '../resources/images/logo/esportsmanager.png')

    icon_path = os.path.join(folder, '../resources/images/logo/esportsmanagertrophy.png')
    button_path = os.path.join(folder, '../resources/images/logo/buttonesm.png')

    sg.theme('Reddit')
    button_color = ('white', 'white')
    default_size = (20, 2)
    default_pad = (300, 15)
    default_font = 'Yukarimobile 25'

    with open(button_path, 'rb') as fp:
        content = fp.read()
        button_encoded = base64.b64encode(content)

    layout = [
        [sg.Image(logo_path)],
        [sg.Button('New Game',
                   font=default_font,
                   button_color=button_color,
                   image_data=button_encoded,
                   pad=default_pad,
                   border_width=0
                   )],
        [sg.Button('Load Game',
                   font=default_font,
                   image_data=button_encoded,
                   pad=default_pad,
                   border_width=0
                   )],
        [sg.Button('Editor', font=default_font, image_data=button_encoded, pad=default_pad, border_width=0)],
        [sg.Button('Exit', font=default_font, image_data=button_encoded, pad=default_pad, border_width=0)]
    ]

    window = sg.Window('eSports Manager', layout, icon=icon_path)
    event, values = window.read()
    window.close()


def new_match():
    match = get_match_obj()

    sg.theme('Reddit')
    team1_names = get_match_info(match.team1)
    team2_names = get_match_info(match.team2)

    layout = [[sg.Text('MATCH INFO', text_color="red", justification="center")],
              [sg.Text(match.team1.name, justification="center"), sg.Text(match.team2.name, justification="center")],
              [sg.Text(match.team1.player_overall, justification="center"),
               sg.Text(match.team2.player_overall, justification="center")],
              [sg.Listbox(values=team1_names, size=(30, 6)),
               sg.Listbox(values=team2_names, size=(30, 6))]
              ]

    window = sg.Window('eSports Manager', layout, icon=icon_encoded)
    event, values = window.read()
    window.close()
