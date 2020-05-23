import random

from src.core.match_live import start_match


if __name__ == '__main__':
    list_ids = list()

    for i in range(20):
        list_ids.append(i)

    # Guarantees that team1 ID is not the same from team2 ID
    team1_id = random.choice(list_ids)
    list_ids.remove(team1_id)
    team2_id = random.choice(list_ids)

    match = start_match(team1_id, team2_id, 1, True, 1, 6)

    print(match.match_id)
    print("Team 1 name: " + match.team1.name)
    for player in match.team1.list_players:
        print(player.first_name + ' ' + player.last_name + ' (' + player.nick_name + ')')
        print('Champion: ' + player.champion.name)

    print("Team 2 name: " + match.team2.name)
    for player in match.team2.list_players:
        print(player.first_name + " " + player.last_name + ' (' + player.nick_name + ')')
        print('Champion: ' + player.champion.name)
