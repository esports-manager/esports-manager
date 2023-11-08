#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2023  Pedrenrique G. Guimarães
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
import threading
from typing import Optional
from queue import Queue
from esm.core.esports.moba.simulation.match_live import MatchLive
from ..team import TeamSimulation
from ..mobamatch import MobaMatch


class MatchManager:
    def __init__(self):
        self.current_game: Optional[MobaMatch] = None
        self.current_live_game: Optional[MatchLive] = None
        self.game_thread: Optional[threading.Thread] = None
        self.is_game_running: bool = False

    def initialize_game(
        self,
        game_id: uuid.UUID,
        championship_id: uuid.UUID,
        team1: TeamSimulation,
        team2: TeamSimulation
    ):
        self.current_game = MobaMatch(
            game_id,
            championship_id,
            team1,
            team2
        )

    def initialize_live_game(
        self,
        game: MobaMatch,
        show_commentary: bool,
        match_speed: int,
        simulation_delay: bool,
        ban_per_team: int,
        difficulty_level: int,
        is_player_match: bool,
        queue: Queue,
        picks_bans_queue: Queue
    ):
        self.current_live_game = MatchLive(
            game,
            show_commentary,
            match_speed,
            simulation_delay,
            ban_per_team,
            difficulty_level,
            is_player_match,
            queue,
            picks_bans_queue
        )

    def get_player_default_lanes(self):
        for team in self.current_game.teams:
            team.get_players_default_lanes()

    def initialize_random_debug_game(self, teams: list, queue=None, picksbans=True, picks_bans_queue=None) -> MatchLive:
        team1 = random.choice(teams)
        teams.remove(team1)
        team2 = random.choice(teams)
        teams.remove(team2)

        self.initialize_game(uuid.uuid4(), uuid.uuid4(), team1, team2)
        self.initialize_live_game(
            self.current_game,
            show_commentary=True,
            match_speed=1,
            simulation_delay=True,
            ban_per_team=5,
            difficulty_level=1,
            is_player_match=False,
            queue=queue,
            picks_bans_queue=picks_bans_queue
        )

        self.get_player_default_lanes()

        if picksbans:
            self.current_live_game.picks_and_bans()

        return self.current_live_game

    def reset_game(self, queue=None, picks_bans_queue=None):
        self.current_live_game.reset_match(queue, picks_bans_queue)

    def reset_team_values(self):
        self.current_live_game.reset_teams()

    def start_game_simulation(self):
        if self.current_live_game is not None:
            self.is_game_running = True
            self.current_live_game.simulation()

    def run_game(self):
        try:
            self.game_thread = threading.Thread(
                target=self.start_game_simulation(), daemon=True
            )
            self.game_thread.start()
        except RuntimeError as e:
            return e
        else:
            return True

    def check_game_running_thread(self):
        if self.game_thread and not self.game_thread.is_alive():
            self.is_game_running = False
