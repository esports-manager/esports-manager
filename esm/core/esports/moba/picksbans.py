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
from queue import Queue

from esm.resources.generator.generate_champions import ChampionGenerator
from esm.core.esports.moba.team import Team
from esm.core.esports.moba.player import MobaPlayer
from esm.core.esports.moba.champion import Champion


class PicksBans:
    """
    Picks and Bans module
    """

    def __init__(
            self,
            team1: Team,
            team2: Team,
            champion_list: list,
            ban_per_team: int = 5,
            difficulty_level=1,
            queue: Queue = None,
    ):
        self.bans_turn = 0
        self.picks_turn = -1
        self.num_bans = 0
        self.num_picks = 0
        self.queue = queue
        self.team1 = team1
        self.team2 = team2
        self.team1_ai = None
        self.team2_ai = None
        self.champion_list = champion_list
        self.ban_per_team = ban_per_team
        self.difficulty_level = difficulty_level
        self.total_bans = int(2 * self.ban_per_team)
        self.picks_order = []
        self.picked_champions = []
        self.banned_champions = []

    # def reset_picks_bans(self, champions_list):
    #     self.picks_order = []
    #     self.picked_champions = []
    #     self.banned_champions = []
    #     self.champion_list = champions_list
    #     if self.team1_ai is not None:
    #         self.team1_ai.reset()
    #     if self.team2_ai is not None:
    #         self.team2_ai.reset()

    def pick(self, player: MobaPlayer, champion: Champion) -> None:
        player.champion = champion
        champion.status = "Picked"
        # self.champion_list.remove(champion)
        self.picked_champions.append(champion)

    def ban(self, team: Team, champion: Champion) -> None:
        team.bans = champion
        champion.status = "Banned"
        # self.champion_list.remove(champion)
        self.banned_champions.append(champion)

    def set_up_player_picks(self):
        self.picks_order = [
            self.team1.list_players[0],
            self.team2.list_players[0],
            self.team2.list_players[1],
            self.team1.list_players[1],
            self.team1.list_players[2],
            self.team2.list_players[2],
            self.team2.list_players[3],
            self.team1.list_players[3],
            self.team1.list_players[4],
            self.team2.list_players[4],
        ]

    def switch_ban_turn(self):
        """
        Starts the ban turn with one team and then passes to the other team to ban.
        Ban turn 0 corresponds to the team1 turn to ban.
        Ban turn 1 corresponds to the team2 turn to ban.
        """
        champion = None
        if self.bans_turn == 0:
            champion = self.get_input(self.team1, self.team2, pick=False)
            team = self.team1
            self.bans_turn = 1
        elif self.bans_turn == 1:
            champion = self.get_input(self.team2, self.team1, pick=False)
            team = self.team2
            self.bans_turn = 0

        if champion is not None:
            self.num_bans += 1
            self.ban(team, champion)

    def switch_pick_turn(self, player):
        """
        Starts the pick turn with one team and then passes to the other team to pick.
        Picks turn 0 corresponds to the team1 turn to pick.
        Picks turn 1 corresponds to the team2 turn to pick.
        """
        champion = None
        if self.picks_turn == 0:
            champion = self.get_input(self.team1, self.team2, pick=True, player=player)
        elif self.picks_turn == 1:
            champion = self.get_input(self.team2, self.team1, pick=True, player=player)

        # Team 1 starts picking. It picks 1 champion, and the turn goes to team 2.
        # Team 2 picks 2 champions. A total of 3 champions were picked, now it's team 1's turn.
        # Team 1 picks 2 champions. 5 Champions were picked in total, so now it's team 2's turn.
        # Team 2 picks 1 champion. Back to ban phase, where team 2 bans its last 2 champions.
        # Team 1 bans the last 2 champions, and the pick phase returns to team2, where they pick 1 more champion.
        # Team 1 picks its last 2 champions, and team2 has the last pick.
        # Normal pick-ban phase in LoL.

        if champion is not None:
            self.pick(player, champion)
            self.num_picks += 1
            self.picks_order.remove(player)

            if self.num_picks in [1, 5, 9]:
                self.picks_turn = 1
            elif self.num_picks in [3, 7]:
                self.picks_turn = 0
            elif self.num_picks == 6:
                self.picks_turn = -1
                self.bans_turn = 1
    
    def ban_turns(self):
        """
        Checks if it's time to switch from picks to bans.
        """
        if self.num_bans == 10:
            self.bans_turn = -1
            self.picks_turn = 1
        elif self.num_bans == 6:
            self.bans_turn = -1
            self.picks_turn = 0

    def pick_turns(self):
        if self.num_picks == 6:
            self.picks_turn = -1
            self.bans_turn = 1
    
    def get_input(self, team, opp_team, pick=True, player=None):
        if team.is_players_team:
            return self.get_player_input()
        else:
            return self.get_ai_input(opp_team, pick=pick, player=player)
    
    def get_ai_input(self, opp_team, pick=True, player=None):
        if self.team1_ai is not None and self.team1_ai.opp_team == opp_team:
            ai = self.team1_ai
        else:
            ai = self.team2_ai

        return ai.get_input(pick, player)

    def get_player_input(self) -> Champion:
        champion = self.queue.get()
        if champion is not isinstance(champion, Champion) and champion in self.banned_champions and self.picked_champions:
            champion = None

        return champion
    
    def picks_bans(self):
        self.set_up_player_picks()

        if self.team1.is_players_team:
            self.team2_ai = PickBanAI(self.team2, self.team1, self.champion_list, self.difficulty_level)
        elif self.team2.is_players_team:
            self.team1_ai = PickBanAI(self.team1, self.team2, self.champion_list, self.difficulty_level)
        else:
            self.team1_ai = PickBanAI(self.team1, self.team2, self.champion_list, self.difficulty_level)
            self.team2_ai = PickBanAI(self.team2, self.team1, self.champion_list, self.difficulty_level)

        while self.num_picks < 10:
            player = self.picks_order[0]

            if self.bans_turn != -1:
                self.switch_ban_turn()
                self.ban_turns()

            if self.picks_turn != -1:
                self.switch_pick_turn(player)


class PickBanAI:
    """
    This is the Pick and Ban AI
    """
    def __init__(self, team, opp_team, champion_list, difficulty_level):
        self.team = team
        self.opp_team = opp_team
        self.champion_list = champion_list
        self.difficulty_level = difficulty_level
        self.best_champions = []
        self.opponents_best_champions = []

        self.get_opponents_best_champions()

    def reset(self):
        self.best_champions = []
        self.opponents_best_champions = []

        self.get_opponents_best_champions()

    def get_input(self, pick=True, player=None):
        if pick is True:
            return self.get_ai_pick_input(player)
        else:
            return self.get_ai_ban_input()

    def get_best_champions(self, player) -> None:
        self.check_champion(player.champions, self.best_champions)

        # If the list is empty, chooses a random champion from the list
        if not self.best_champions:
            self.best_champions.append(random.choice(self.champion_list))

    def get_ai_pick_input(self, player):
        self.get_best_champions(player)

        return random.choice(self.best_champions)

    def get_ai_ban_input(self) -> Champion:
        """
        Returns the champions that the AI is going to ban, based on the best champions on the opponent's team player pool.

        Still a naive implementation, should consider best players above everything.
        """
        return (
            random.choice(self.opponents_best_champions)
            if self.opponents_best_champions
            else random.choice(self.champion_list)
        )

    def check_champion(self, list_ch, second_list):
        second_list.clear()

        for champion in list_ch:
            ch = ChampionGenerator()
            ch.champions_list = self.champion_list
            ch = ch.get_champion_by_id(champion["id"], self.champion_list)
            second_list.append(ch)

        self.check_champion_used()

    def get_opponents_best_champions(self) -> None:
        """
        Gets the list of the best champions from the opponent team.
        """
        # Adds all the best champions to the list of best champions
        for player in self.team.list_players:
            self.check_champion(player.champions, self.opponents_best_champions)

        # If the list is empty, chooses a random champion from the list
        if not self.opponents_best_champions:
            self.opponents_best_champions.append(random.choice(self.champion_list))

    def check_champion_used(self):
        for champion in self.champion_list:
            if champion.status in ["Banned", "Picked"]:
                self.champion_list.remove(champion)
                if champion in self.best_champions:
                    self.best_champions.remove(champion)
                if champion in self.opponents_best_champions:
                    self.opponents_best_champions.remove(champion)
