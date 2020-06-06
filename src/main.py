import random
import PySimpleGUIQt as sg

from src.core.match_live import start_match


def get_match_info(team):
    team_names = []
    for player in team.list_players:
        name = player.first_name + ' ' + player.last_name + ' ' + str(player.skill)
        team_names.append(name)

    return team_names


if __name__ == '__main__':
    list_ids = list()

    for i in range(20):
        list_ids.append(i)

    # Guarantees that team1 ID is not the same from team2 ID
    team1_id = random.choice(list_ids)
    list_ids.remove(team1_id)
    team2_id = random.choice(list_ids)

    match = start_match(team1_id, team2_id, 1, True, 1, 6)

    sg.theme('Reddit')
    team1_names = get_match_info(match.team1)
    team2_names = get_match_info(match.team2)

    layout = [[sg.Text('MATCH INFO', text_color="red", justification="center")],
              [sg.Text(match.team1.name, justification="center"), sg.Text(match.team2.name, justification="center")],
              [sg.Listbox(values=team1_names, size=(30, 6)),
               sg.Listbox(values=team2_names, size=(30, 6))]
              ]

    window = sg.Window('eSports Manager', layout)
    event, values = window.read()
    window.close()

