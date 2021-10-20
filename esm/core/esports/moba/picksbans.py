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
        self.champion_list = champion_list
        self.ban_per_team = ban_per_team
        self.difficulty_level = difficulty_level
        self.total_bans = int(2 * self.ban_per_team)
        self.picks_order = []
        self.picked_champions = []
        self.banned_champions = []
        self.ai_ban_champions_team1 = None
        self.ai_ban_champions_team2 = None
        self.ai_ban_champions = []
        self.ai_pick_champions = None

    def pick(self, player: MobaPlayer, champion: Champion) -> None:
        player.champion = champion
        self.picked_champions.append(champion)
    
    def ban(self, team: Team, champion: Champion) -> None:
        team.bans = champion
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
            champion = self.get_input(self.team2, self.team2, pick=False)
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
    
    def get_player_input(self) -> Champion:
        return self.queue.get()

    def get_ai_pick_champions(self, player) -> None:
        self.ai_pick_champions.clear()
        champions_id = [champion_id for champion_id in player.champions]

        for ch_id in champions_id:
            champion = ChampionGenerator().get_champion_by_id(ch_id["id"], self.champion_list)
            self.ai_pick_champions.append(champion)

        self.check_champion_used(self.ai_pick_champions)

        # If the list is empty, chooses a random champion from the list
        if not self.ai_pick_champions:
            self.ai_pick_champions.append(random.choice(self.champion_list))

    def get_ai_input(self, opp_team, pick=True, player=None) -> Champion:
        """
        Gets the AI pick or ban.
        """
        if pick is True:
            return self.get_ai_pick_input(player)
        else:
            return self.get_ai_ban_input(opp_team)
    
    def get_ai_pick_input(self, player) -> Champion:
        if self.ai_pick_champions is None:
            self.ai_pick_champions = []

        self.get_ai_pick_champions(player)

        return random.choice(self.ai_pick_champions)
    
    def check_champion_used(self, ch_list):
        """
        Checks if the champion was picked or banned before
        """
        for ch in ch_list:
            if ch in self.banned_champions or ch in self.picked_champions:
                ch_list.remove(ch)
    
    def get_opponents_best_champions(self, team) -> None:
        """
        Gets the list of the best champions from the opponent team.
        """
        self.ai_ban_champions.clear()
        champions_id = []

        # Adds all the best champions to the list of champion_ids
        for player in team.list_players:
            for champion in player.champions:
                champions_id.append(champion)
        
        # Transforms champion dictionaries in objects
        for ch_id in champions_id:
            champion = ChampionGenerator().get_champion_by_id(ch_id["id"], self.champion_list)
            self.ai_ban_champions.append(champion)
        
        self.check_champion_used(self.ai_ban_champions)
        
        # If the list is empty, chooses a random champion from the list
        if not self.ai_ban_champions:
            self.ai_ban_champions.append(random.choice(self.champion_list))

        if team == self.team1:
            self.ai_ban_champions_team1 = self.ai_ban_champions.copy()
        elif team == self.team2:
            self.ai_ban_champions_team2 = self.ai_ban_champions.copy()

        self.ai_ban_champions.clear()

    def get_ai_ban_input(self, opp_team) -> Champion:
        """
        Returns the champions that the AI is going to ban, based on the best champions on the opponent's team player pool.

        Still a naive implementation, should consider best players above everything.
        """
        if self.ai_ban_champions is None:
            self.ai_ban_champions = []

        if opp_team == self.team1:
            self.ai_ban_champions = self.ai_ban_champions_team1
        elif opp_team == self.team2:
            self.ai_ban_champions = self.ai_ban_champions_team2

        champion = random.choice(self.ai_ban_champions)
        
        if champion is None:
            random.choice(self.champion_list)
        
        return champion
    
    def picks_bans(self):
        self.set_up_player_picks()

        if self.team1.is_players_team:
            self.get_opponents_best_champions(self.team1)
        elif self.team2.is_players_team:
            self.get_opponents_best_champions(self.team2)
        else:
            self.get_opponents_best_champions(self.team1)
            self.get_opponents_best_champions(self.team2)

        while self.num_picks < 10:
            player = self.picks_order[0]

            if self.ban_turns != -1:
                self.switch_ban_turn()
                self.ban_turns()

            if self.picks_turn != -1:
                self.switch_pick_turn(player)

