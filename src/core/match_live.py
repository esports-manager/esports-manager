import random

from .event import Event
from .match import Match
from ..resources.utils import load_list_from_json
from .pre_match import get_teams_dictionaries, create_team_object, create_champion_object
from time import sleep


class MatchLive:
    def __init__(self, match: Match, show_commentary, match_speed):
        self.match = match
        self.game_time = 0.0
        self.first_blood = False
        self.victorious_team = None
        self.show_commentary = show_commentary
        self.match_speed = match_speed
        self.is_match_over = False

    def picks_and_bans(self) -> None:
        """
        Dummy picks and bans implementation. Will be changed in the future.
        """
        champion_list = load_list_from_json('champions.json')

        # TODO: implement proper picks an bans

        # Testing, picking random champions for each player
        for i in range(2):
            for player in self.match.teams[i].list_players:
                champion_dict = random.choice(champion_list)
                champion_list.remove(champion_dict)
                champion = create_champion_object(champion_dict)
                player.champion = champion

    def get_speed(self) -> int:
        if self.match_speed == 1:
            return 5
        elif self.match_speed == 2:
            return 10
        elif self.match_speed == 3:
            return 15

    def calculate_both_teams_win_prob(self) -> None:
        total_prob = sum(
            team.player_overall + team.champion_overall + team.points for team in self.match.teams
        )

        for team in self.match.teams:
            team.win_prob = (team.player_overall + team.champion_overall + team.points) / total_prob

    def get_events(self, events):
        """
        This method is used to get the events of the game, and add them to a list of events.
        I don't really like this implementation, it is really clunky and ugly, but I just want to see if it works.
        I can rewrite it later once I get better ideas for it.
        """
        if self.game_time == 0.0:
            events.append(Event(1, 'START_MATCH', 1, self.get_commentaries('START_MATCH'), 0))
        elif self.game_time == 1.0:
            events.clear()
            events.append(Event(2, 'INVADE', 1, self.get_commentaries('INVADE'), 0))
            events.append(Event(3, 'KILL', 1, self.get_commentaries('KILL'), 5))
        elif self.game_time == 2.0:
            events.remove(0)
            events.append(Event(4, 'TEAM_FIGHT', 1, self.get_commentaries('TEAM_FIGHT'), 10))
            events.append(Event(5, 'GANK', 2, self.get_commentaries('GANK'), 5))
            events.append(Event(6, 'LANE_FIGHT', 2, self.get_commentaries('LANE_FIGHT'), 5))
            events.append()
        elif self.game_time == 15.0:
            events.append(Event(7, 'TOWER_ASSAULT', 1, self.get_commentaries('TOWER_ASSAULT'), 15))
        elif self.game_time == 20.0:
            events.append(Event(8, 'MAJOR_JUNGLE', 2, self.get_commentaries('MAJOR_JUNGLE'), 15))

        if self.match.team1.is_inhib_exposed():
            events.append(Event(9, 'INHIBITOR_ASSAULT_TEAM1', 3, self.get_commentaries('INHIBITOR_ASSAULT_TEAM1'), 15))
        if self.match.team2.is_inhib_exposed():
            events.append(Event(10, 'INHIBITOR_ASSAULT_TEAM2', 3, self.get_commentaries('INHIBITOR_ASSAULT_TEAM2'), 15))
        if self.match.team1.are_all_towers_up() is False or self.match.team2.are_all_towers_up():
            events.append(Event(11, 'NEXUS_ASSAULT', 5, self.get_commentaries('NEXUS_ASSAULT'), 15))

    def get_commentaries(self, event_name):
        """
        This method gets commentaries for specific events.
        I don't like this implementation either, and it will be changed in the future for sure. I know there
        is a better way to do this, but it takes a little while to implement and I have to think it through.
        :param event_name:
        :return:
        """
        commentaries = []
        return commentaries

    def match_loop(self) -> None:
        while self.is_match_over is False:
            self.calculate_both_teams_win_prob()

            sleep(self.get_speed())


def initialize_match(team1_id: int,
                     team2_id: int,
                     match_id: int,
                     ch_id: int) -> Match:
    """
    Instantiate each object that is going to be used by the match, returning
    the match object.
    :param team1_id:
    :param team2_id:
    :param match_id:
    :param ch_id:+
    :return:
    """
    # Gets both lists to use it on the appropriate functions
    team_list = load_list_from_json('teams.json')
    player_list = load_list_from_json('players.json')

    # Creates both teams dictionaries to create their objects
    team1_dict, team2_dict = get_teams_dictionaries(team1_id, team2_id, team_list)

    # Instantiate team objects, creating players' objects as well
    team1 = create_team_object(team1_dict, player_list)
    team2 = create_team_object(team2_dict, player_list)

    return Match(match_id, ch_id, team1, team2)


def get_live_obj_test() -> MatchLive:
    """
    This function is used to get random teams from the db, and then get matchlive obj.
    In the future this might be trashed.
    :return:
    """
    list_ids = [i for i in range(20)]

    # Guarantees that team1 ID is not the same from team2 ID
    team1_id = random.choice(list_ids)
    list_ids.remove(team1_id)
    team2_id = random.choice(list_ids)

    live = MatchLive(initialize_match(team1_id, team2_id, 1, 1), True, 1)
    live.picks_and_bans()

    return live


def start_match(team1_id: int,
                team2_id: int,
                match_id: int,
                show_commentary: bool,
                match_speed: int,
                ch_id: int) -> Match:

    match = initialize_match(team1_id, team2_id, match_id, ch_id)

    live = MatchLive(match, show_commentary, match_speed)
    live.picks_and_bans()

    # live.match_loop()

    return match
