from core.team import Team
from core.player import Player
from core.champion import Champion
from core.match import Match

names_team = [
    "Impact",
    "bengi",
    "Faker",
    "Piglet",
    "PoohManDuH",
    "Looper",
    "DanDy",
    "PawN",
    "imp",
    "Mata",
]
skill_team = [92, 93, 95, 92, 90, 90, 92, 93, 90, 91]
team_name = ["SKT", "SSW"]

names_champions = [
    "Jax",
    "Lee Sin",
    "Zed",
    "Vayne",
    "Zyra",
    "Singed",
    "Rengar",
    "Talon",
    "Twitch",
    "Thresh",
]
skill_champions = [75, 85, 80, 87, 76, 60, 82, 76, 88, 90]

players_team1 = []
players_team2 = []

teams = []

players = []


def generate_player():
    for i in range(10):
        # Defining players here
        player_name = names_team[i]
        player_skill = skill_team[i]
        player = Player(player_name, player_skill)

        # Defining champion for each player
        champion_name = names_champions[i]
        champion_skill = skill_champions[i]
        champion = Champion(champion_name, champion_skill)

        # Assigns the champion to the player
        player.champion = champion
        players.append(player)

    for i in range(5):
        players_team1.append(players[i])
        players_team2.append(players[i + 5])


def generate_team(list_player, i):
    teamname = team_name[i]
    team = Team(teamname, list_player)
    teams.append(team)


generate_player()
generate_team(players_team1, 0)
generate_team(players_team2, 1)

match = Match(1, 1, teams[0], teams[1], True, 1)
match.match_live()
