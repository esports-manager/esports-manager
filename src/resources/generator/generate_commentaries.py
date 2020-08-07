def get_gank_comm(player_gank: str, lane: str) -> list:
    return [
        str(player_gank + ' is going to gank ' + lane),
        str(player_gank + ' is moving towards ' + lane),
        str(player_gank + ' prepares a gank in ' + lane + ' lane')
    ]


def get_invade_comm(team_invade: str) -> list:
    return [
        str(team_invade + ' decides to invade!'),
        str(team_invade + ' is sneaking into the opponent\'s side of the map!'),
        str(team_invade + ' wants to start a team fight early in the game!')
    ]


def get_team_fight_comm(team1: str, team2: str) -> list:
    return [
        str(team1 + ' starts a team fight!'),
        str(team1 + ' gets aggressive towards ' + team2 + '!'),
        str('A team fight breaks out! Maybe ' + team1 + ' is favored! ' + team2 + ' looks very shaky!')
    ]


def get_tower_assault(team1: str, team2: str, lane: str):
    return [
        str(team1 + ' is attacking ' + team2 + '\'s ' + lane + 'lane exposed tower!'),
        str(team2 + '\'s base is under attack!')
    ]