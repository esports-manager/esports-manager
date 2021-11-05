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
import uuid
import time
import math
import gc

from queue import Queue
from typing import Union, Tuple

from .picksbans import PicksBans
from .team import Team
from .match import Match
from .mobaevent import MobaEventHandler
from esm.resources.generator.generate_champions import ChampionGenerator


class MatchLive:
    """
    The MatchLive class is the one that contains information about the live match events.
    It receives a Match object with all the information from teams and players, and defines all the other
    match simulation details.

    The simulation, however, is delegated to the MobaEventHandler object, that can only look to events and the
    current game state. The MatchLive only provides needed information for the simulation to take place, and
    in the end gets the winning team from the EventHandler.
    """

    def __init__(
            self, match: Match,
            show_commentary: bool = True,
            match_speed: int = 1,
            simulate: bool = True,
            ban_per_team: int = 5,
            difficulty_level: int = 1,
            is_player_match: bool = False,
            queue: Queue = None,
            picks_bans_queue: Queue = None,
    ):
        self.match = match
        self.game_time = 0.0
        self.victorious_team = None
        self.show_commentary = show_commentary
        self.match_speed = match_speed
        self.is_match_over = False
        self.bans = []
        self.simulate = simulate
        self.event_handler = MobaEventHandler(self.show_commentary, queue)
        self.champions = ChampionGenerator()
        self.champions.get_champions()
        self.ban_per_team = ban_per_team
        self.difficulty_level = difficulty_level
        self.picks_bans_queue = picks_bans_queue
        self.picks_bans = PicksBans(
            self.match.team1,
            self.match.team2,
            self.champions.champions_obj,
            self.ban_per_team,
            self.difficulty_level,
            self.picks_bans_queue,
        )
        self.is_player_match = is_player_match

    def reset_match(self, queue=None, picks_bans_queue=None) -> None:
        self.reset_teams()
        self.game_time = 0.0
        self.victorious_team = None
        self.is_match_over = False
        self.event_handler = MobaEventHandler(self.show_commentary, queue)
        self.champions.get_champions()
        self.picks_bans.champion_list = self.champions.champions_obj
        self.picks_bans.queue = picks_bans_queue
        gc.collect()

    def check_is_player_match(self) -> bool:
        return any(team.is_players_team for team in self.match.teams)

    def reset_teams(self) -> None:
        for team in self.match.teams:
            team.reset_values()

    def picks_and_bans(self) -> None:
        """
        Dummy picks and bans implementation. Will be changed in the future.

        Probably picks and bans should be handled differently in the UI. But I need to come up
        with a general implementation that can be used regardless of the UI.
        """
        self.is_player_match = self.check_is_player_match()
        self.picks_bans.picks_bans()

    def calculate_both_teams_win_prob(self) -> None:
        """
        Calculates both teams Win probabilities. This is used for internal match simulation calculations. The winning
        team will always have a significant advantage over the losing team.
        """
        total_prob = sum(team.total_skill for team in self.match.teams)

        for team in self.match.teams:
            team.win_prob = team.total_skill / total_prob

    def increment_game_time(self, quantity):
        """
        Defines how slowly time passes on the match. I found 0.5 to be the most realistic time simulation.
        """
        self.game_time += quantity

    def get_tower_number(self) -> int:
        """
        Gets the amount of towers in the game. If neither team has any towers, the game stops trying to generate the
        Tower Assault events.
        """
        return sum(sum(team.towers.values()) for team in self.match.teams)

    def which_team_nexus_exposed(self) -> Union[Tuple[Team, Team], Team, None]:
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

    def check_match_over(self) -> None:
        """
        Checks if one of the nexus is down and terminates the simulation
        """
        for team in self.match.teams:
            if team.nexus == 0:
                self.is_match_over = True

    def winning_team(self) -> None:
        """
        Assigns the winner to the team that still has the nexus up
        """
        for team in self.match.teams:
            if team.nexus == 1:
                self.victorious_team = team
                self.match.victorious_team = self.victorious_team

    def is_any_inhib_open(self) -> bool:
        """
        Checks for open inhibitors, to decide whether a base tower or nexus can be attacked
        """
        for team in self.match.teams:
            open_inhibs = team.get_exposed_inhibs()
            if open_inhibs:
                return True
        return False

    def simulation(self) -> None:
        """
        Match simulation method. Starts the while loop.
        """
        # if self.show_commentary:
        #     self.event_handler.load_commentaries_file()

        while not self.is_match_over:
            self._run_match()
        self.winning_team()

    def _run_match(self):
        """
        Runs the match simulation logic
        """
        self.calculate_both_teams_win_prob()
        self.event_handler.get_game_state(
            self.game_time,
            self.which_team_nexus_exposed(),
            self.is_any_inhib_open(),
            self.get_tower_number(),
        )
        self.event_handler.generate_event(self.game_time)
        self.event_handler.event.calculate_event(
            self.match.team1, self.match.team2, self.which_team_nexus_exposed()
        )
        self.check_match_over()

        if not self.is_match_over:
            self.increment_game_time(0.5)

        if self.simulate:
            time.sleep(self.match_speed)


class MatchSeries:
    def __init__(
            self,
            team1,
            team2,
            championship_id,
            best_of=3,
            show_commentary: bool = True,
            match_speed: int = 1,
            simulate: bool = True,
            ban_per_team: int = 5,
            difficulty_level: int = 1,
            is_player_match: bool = False
    ):
        self.championship_id = championship_id
        self.team1 = team1
        self.team2 = team2
        self.best_of = best_of

        # If there is a chance to draw a match
        self.drawable = self.best_of % 2 == 0

        # How many wins a team must have to be declared winner
        self.required_wins = math.ceil(self.best_of / 2)
        if self.drawable:
            self.required_wins = self.required_wins + 1

        self.matches = []
        self.team_wins = [0, 0]

        # MatchLive related
        self.show_commentary = show_commentary
        self.match_speed = match_speed
        self.simulate = simulate
        self.is_player_match = is_player_match
        self.ban_per_team = ban_per_team
        self.difficulty_level = difficulty_level

    def is_series_over(self):
        if len(self.matches) == self.best_of:
            return True

        return self.required_wins in self.team_wins

    def get_winning_team(self):
        if self.team_wins[0] > self.team_wins[1]:
            return self.team1
        elif self.team_wins[1] > self.team_wins[0]:
            return self.team2
        else:
            return self.team1, self.team2

    def get_matches(self):
        if not self.is_series_over():
            teams = [self.team1, self.team2]
            # Randomly assign teams to a side, so we can have a rotation of team sides
            random.shuffle(teams)

            self.matches.append(
                MatchLive(
                    Match(uuid.uuid4(), self.championship_id, teams[0], teams[1]),
                    self.show_commentary,
                    self.match_speed,
                    self.simulate,
                    self.ban_per_team,
                    self.difficulty_level,
                    self.is_player_match,
                )
            )

    def assign_match_winner(self, match):
        if match.victorious_team.name == self.team1.name:
            self.team_wins[0] += 1
        else:
            self.team_wins[1] += 1


def initialize_match(team1, team2, ch_id) -> MatchLive:
    """
    Instantiate each object that is going to be used by the match, returning
    the match object.
    :param team1:
    :param team2:
    :param ch_id:
    :return:
    """

    match = Match(uuid.uuid4().int, ch_id, team1, team2)
    return MatchLive(match, True, 1)
