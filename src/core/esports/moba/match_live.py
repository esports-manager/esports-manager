#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2021  Pedrenrique G. Guimarães
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

import random
import time

from src.core.esports.moba.match import Match
from src.core.esports.moba.mobaevent import MobaEventHandler
from src.resources.generator.generate_champions import ChampionGenerator


class MatchLive:
    """
    The MatchLive class is the one that contains information about the live match events.
    It receives a Match object with all the information from teams and players, and defines all the other
    match simulation details.

    The simulation, however, is delegated to the MobaEventHandler object, that can only look to events and the
    current game state. The MatchLive only provides needed information for the simulation to take place, and
    in the end gets the winning team from the EventHandler.
    """
    def __init__(self, match: Match, show_commentary, match_speed, simulate=True):
        self.match = match
        self.game_time = 0.0
        self.victorious_team = None
        self.show_commentary = show_commentary
        self.match_speed = match_speed
        self.is_match_over = False
        self.simulate = simulate
        self.event_handler = MobaEventHandler()
        self.champions = ChampionGenerator()

    def picks_and_bans(self) -> None:
        """
        Dummy picks and bans implementation. Will be changed in the future.

        Probably picks and bans should be handled differently in the UI. But I need to come up
        with a general implementation that can be used regardless of the UI.
        """
        self.champions.get_champions()
        for team in self.match.teams:
            for player in team.list_players:
                player.get_default_lane()
                champion = random.choice(self.champions.champions_obj)
                self.champions.champions_obj.remove(champion)
                player.champion = champion

    def calculate_both_teams_win_prob(self) -> None:
        """
        Calculates both teams Win probabilities. This is used for internal match simulation calculations. The winning
        team will always have a significant advantage over the losing team.
        """
        total_prob = sum(
            team.total_skill for team in self.match.teams
        )

        for team in self.match.teams:
            team.win_prob = team.total_skill / total_prob

    def increment_game_time(self, quantity):
        """
        Defines how slowly time passes on the match. I found 0.5 to be the most realistic time simulation.
        """
        self.game_time += quantity

    def get_tower_number(self):
        """
        Gets the amount of towers in the game. If neither team has any towers, the game stops trying to generate the
        Tower Assault events.
        """
        return sum(sum(team.towers.values()) for team in self.match.teams)

    def which_team_nexus_exposed(self):
        """
        Gets the exposed nexus from one or both of the teams.
        """
        if self.match.team1.is_nexus_exposed():
            if self.match.team2.is_nexus_exposed():
                return self.match.team1, self.match.team2
            return self.match.team1
        elif self.match.team2.is_nexus_exposed():
            return self.match.team2
        else:
            return None

    def check_match_over(self):
        """
        Checks if one of the nexus is down and terminates the simulation
        """
        for team in self.match.teams:
            if team.nexus == 0:
                self.is_match_over = True

    def winning_team(self):
        """
        Assigns the winner to the team that still has the nexus up
        """
        for team in self.match.teams:
            if team.nexus == 1:
                self.victorious_team = team

    def is_any_inhib_open(self) -> bool:
        """
        Checks for open inhibitors, to decide whether a base tower or nexus can be attacked
        """
        for team in self.match.teams:
            open_inhibs = team.get_exposed_inhibs()
            if open_inhibs:
                return True
        return False

    def simulation(self):
        """
        Match simulation method. Starts the while loop.
        """
        if self.show_commentary:
            self.event_handler.load_commentaries_file()

        while not self.is_match_over:
            self.calculate_both_teams_win_prob()
            self.event_handler.get_game_state(self.game_time,
                                              self.which_team_nexus_exposed(),
                                              self.is_any_inhib_open(),
                                              self.get_tower_number())
            self.event_handler.generate_event(self.game_time)
            self.event_handler.event.calculate_event(self.match.team1,
                                                     self.match.team2,
                                                     self.which_team_nexus_exposed())
            self.check_match_over()

            if not self.is_match_over:
                self.increment_game_time(0.5)

            if self.simulate:
                time.sleep(self.match_speed)

        self.winning_team()
        print(self.victorious_team, 'Won the match!')


def initialize_match(team1,
                     team2,
                     ch_id):
    """
    Instantiate each object that is going to be used by the match, returning
    the match object.
    :param team1:
    :param team2:
    :param ch_id:
    :return:
    """

    match = Match(ch_id, team1, team2)
    return MatchLive(match, True, 1)
