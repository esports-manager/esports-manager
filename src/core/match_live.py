import random

from src.core.champion import Champion
from src.core.event import Event
from src.core.match import Match
from src.core.player import MobaPlayer
from src.core.team import Team
from src.resources.utils import get_dict_list


def get_team(team_id, list_teams) -> dict:
    """
    Extracts the desired team from the list of teams, returning the team's
    dictionary
    :param team_id:
    :param list_teams:
    :return: team dictionary
    """
    obtained_team = None

    for team in list_teams:
        if team["id"] == team_id:
            obtained_team = team
            return obtained_team

    if obtained_team is None:
        raise Exception("Team was not found!")


def get_teams_dictionaries(team1_id, team2_id, list_of_teams) -> dict:
    """
    Used to return both teams dictionaries, based on their team IDs
    :param team1_id:
    :param team2_id:
    :param list_of_teams:
    :return:
    """
    team1 = get_team(team1_id, list_of_teams)
    team2 = get_team(team2_id, list_of_teams)

    return team1, team2


def create_team_object(team_dict, all_players) -> Team:
    """
    Creates the team object based on the Team class. It also gets the roster
    and uses the get_roster() function to create the players list
    :param team_dict:
    :param all_players:
    :return:
    """
    team_id = team_dict["id"]
    name = team_dict["name"]
    list_of_players = team_dict["roster_id"]
    roster = get_roster(list_of_players, all_players)

    team = Team(team_id, name, roster)

    return team


def create_player_object(player_dict) -> MobaPlayer:
    """
    Creates the player object
    :param player_dict:
    :return:
    """
    player_id = player_dict["id"]
    first_name = player_dict["first_name"]
    last_name = player_dict["last_name"]
    nationality = player_dict["nationality"]
    nick_name = player_dict["nick_name"]
    skill = player_dict["skill"]

    player = MobaPlayer(player_id, nationality, first_name, last_name, nick_name, skill)

    return player


def create_champion_object(champion_dict) -> Champion:
    """
    Creates the champion object to insert it on the player choice
    :param champion_dict: champion dictionary obtained from json file
    :return: champion object
    """
    champion_id = champion_dict["id"]
    name = champion_dict["name"]
    skill = champion_dict["skill"]

    champion = Champion(champion_id, name, skill)

    return champion


def get_roster(list_of_players, all_players) -> list:
    """
    Searches for each player ID on the player's list, creates the player
    object based on the player dictionary, returning this object
    :param list_of_players: list of players from the roster
    :param all_players: entire player list database
    :return: list of players
    """
    roster = list()

    # Is there a more pythonic way to do this? List comprehensions would solve it?
    for player_id in list_of_players:
        for player_dict in all_players:
            if player_dict["id"] == player_id:
                player = create_player_object(player_dict)
                roster.append(player)
                break

    return roster


def initialize_match(team1_id, team2_id, match_id, show_commentary, match_speed, ch_id) -> Match:
    """
    Instantiate each object that is going to be used by the match, returning
    the match object.
    :param team1_id:
    :param team2_id:
    :param match_id:
    :param show_commentary:
    :param match_speed:
    :param ch_id:
    :return:
    """
    # Gets both lists to use it on the appropriate functions
    team_list = get_dict_list("./resources/db/teams.json")
    player_list = get_dict_list("./resources/db/players.json")

    # Creates both teams dictionaries to create their objects
    team1_dict, team2_dict = get_teams_dictionaries(team1_id, team2_id, team_list)

    # Instantiate team objects, creating players' objects as well
    team1 = create_team_object(team1_dict, player_list)
    team2 = create_team_object(team2_dict, player_list)

    # Instantiate a match
    match = Match(match_id, ch_id, team1, team2, show_commentary, match_speed)

    return match


def picks_and_bans(match):
    """
    Dummy picks and bans implementation. Will be changed in the future.
    :param match:
    :return:
    """
    champion_list = get_dict_list("./resources/db/champions.json")

    # TODO: implement proper picks an bans

    # Testing, picking random champions for each player
    for i in range(2):
        for player in match.teams[i].list_players:
            champion_dict = random.choice(champion_list)
            champion_list.remove(champion_dict)
            champion = create_champion_object(champion_dict)
            player.champion = champion


def get_match_obj() -> Match:
    """
    This function is used to get random teams from the db, and then get match obj.
    In the future this might be trashed.
    :return:
    """
    list_ids = [i for i in range(20)]

    # Guarantees that team1 ID is not the same from team2 ID
    team1_id = random.choice(list_ids)
    list_ids.remove(team1_id)
    team2_id = random.choice(list_ids)

    match = start_match(team1_id, team2_id, 1, True, 1, 6)

    return match


def initialize_event_list() -> list:
    events = ["START_MATCH"]
    return events


def add_events(match, events):
    if match.game_time == 1.0:
        events.remove("START_MATCH")
        events.append("INVADE")
    elif match.game_time == 2.0:
        events.remove("INVADE")
        events.append("GANK")
        events.append("TEAM_FIGHT")
    elif match.game_time == 15.0:
        events.append("TOWER_ASSAULT")
        events.append("MAJOR_JUNGLE")
        events.remove("GANK")
    elif match.game_time == 20.0:
        events.append("SUPER_JUNGLE")

    if not match.team1.are_all_towers_up() or not match.team2.are_all_towers_up():
        events.append("INHIBITOR_ASSAULT")

    if not match.team1.are_all_inhibitors_up() or not match.team2.are_all_inhibitors_up():
        events.append("BASE_TOWERS_ASSAULT")

    if not match.team1.is_tower_up("base") or not match.team2.is_tower_up("base"):
        events.append("BASE_ASSAULT")


def get_event(match, events) -> Event:
    add_events(match, events)

    # TODO: this cannot be randomly chosen, there should be some weight calculation going on
    event = Event(random.choice(events))

    return event


def define_atk_team(match):
    prob = random.gauss(0, 1)

    if match.team1.points > match.team2.points:
        if -1 < prob < 1:
            atk_team = match.team1
            def_team = match.team2
        else:
            atk_team = match.team2
            def_team = match.team1
    elif match.team2.points > match.team1.points:
        if -1 < prob < 1:
            atk_team = match.team2
            def_team = match.team1
        else:
            atk_team = match.team1
            def_team = match.team2
    else:
        atk_team = random.choice(match.teams)
        if atk_team == match.team1:
            def_team = match.team2
        else:
            def_team = match.team1

    return atk_team, def_team


def evaluate_event(match, event):
    if event.name == "START_MATCH":
        print("Match is starting between {} and {}".format(match.team1.name, match.team2.name))
    elif event.name == "INVADE":
        match.event_invade()
    elif event.name == "GANK":
        match.event_gank()
    elif event.name == "TEAM_FIGHT":
        atk_team, def_team = define_atk_team(match)
        match.event_team_fight(atk_team, def_team)
    elif event.name == "TOWER_ASSAULT":
        match.event_tower_assault()
    elif event.name == "MAJOR_JUNGLE":
        match.event_major_jungle()
    elif event.name == "SUPER_JUNGLE":
        match.event_super_jungle()
    elif event.name == "INHIBITOR_ASSAULT":
        match.event_inhib_assault()
    elif event.name == "BASE_TOWERS_ASSAULT":
        match.event_base_towers_assault()
    elif event.name == "BASE ASSAULT":
        match.event_base_assault()

    match.game_time += 1


def event_team_fight(atk_team, def_team):
    prob = random.gauss(0, 1)

    duel_pl_factor = atk_team.player_overall / def_team.player_overall
    duel_ch_factor = atk_team.champion_overall / def_team.champion_overall


def start_match(team1_id, team2_id, match_id, show_commentary, match_speed, ch_id) -> Match:
    match = initialize_match(team1_id, team2_id, match_id, show_commentary, match_speed, ch_id)
    picks_and_bans(match)

    events = initialize_event_list()

    event = get_event(match, events)

    # TODO: implement match loop

    return match
