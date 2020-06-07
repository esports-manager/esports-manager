import random
import PySimpleGUIQt as sg

from src.core.match_live import get_match_obj, get_match_info

if __name__ == '__main__':
    match = get_match_obj()

    sg.theme('Reddit')
    team1_names = get_match_info(match.team1)
    team2_names = get_match_info(match.team2)

    layout = [[sg.Text('MATCH INFO', text_color="red", justification="center")],
              [sg.Text(match.team1.name, justification="center"), sg.Text(match.team2.name, justification="center")],
              [sg.Text(match.team1.avg_player_skill, justification="center"),
               sg.Text(match.team2.avg_player_skill, justification="center")],
              [sg.Listbox(values=team1_names, size=(30, 6)),
               sg.Listbox(values=team2_names, size=(30, 6))]
              ]

    window = sg.Window('eSports Manager', layout)
    event, values = window.read()
    window.close()

