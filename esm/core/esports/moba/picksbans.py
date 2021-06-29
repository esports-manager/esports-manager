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
from esm.resources.generator.generate_champions import ChampionGenerator
import random

from esm.core.esports.moba.team import Team
from esm.core.esports.moba.player import MobaPlayer
from esm.core.esports.moba.champion import Champion


class PicksBans:
    """
    Picks and Bans module
    """

    def __init__(self, team1: Team, team2: Team, champion_list: list, ban_per_team: int = 5, difficulty_level=1):
        self.bans_turn = 0
        self.picks_turn = -1
        self.num_bans = 0
        self.num_picks = 0
        self.team1 = team1
        self.team2 = team2
        self.champion_list = champion_list
        self.ban_per_team = ban_per_team
        self.difficulty_level = difficulty_level
        self.total_bans = int(2 * self.ban_per_team)
        self.picks_order = []
        self.ai_ban_champions = None
        self.ai_pick_champions = None

    def pick(self, player: MobaPlayer, champion: Champion) -> None:
        player.champion = champion
        self.champion_list.remove(champion)
    
    def ban(self, team: Team, champion: Champion) -> None:
        team.bans = champion
        for ch in self.champion_list:
            if champion.champion_id == ch.champion_id:
                self.champion_list.remove(ch)
                break

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
            self.ban(self.team1, champion)
            self.bans_turn = 1
        elif self.bans_turn == 1:
            champion = self.get_input(self.team2, self.team2, pick=False)
            self.ban(self.team2, champion)
            self.bans_turn = 0

        if champion is not None:
            self.num_bans += 1

    def switch_pick_turn(self, player):
        """
        Starts the pick turn with one team and then passes to the other team to pick.
        Picks turn 0 corresponds to the team1 turn to ban.
        Picks turn 1 corresponds to the team2 turn to ban.
        """
        champion = None
        if self.picks_turn == 0:
            champion = self.get_input(self.team1, self.team2, pick=True, player=player)
        elif self.picks_turn == 1:
            champion = self.get_input(self.team2, self.team1, pick=True, player=player)

        if self.num_picks == 1 or self.num_picks == 5 or self.num_picks == 9:
            self.picks_turn = 1
        elif self.num_picks == 3 or self.num_picks == 7:
            self.picks_turn = 0 
        elif self.num_picks == 6:
            self.picks_turn = -1
            self.bans_turn = 1

        if champion is not None:
            self.pick(player, champion)
            self.num_picks += 1
            self.picks_order.remove(player)
    
    def ban_turns(self):
        """
        Checks if it's time to switch from picks to bans.
        """
        if self.num_bans == 6:
            self.bans_turn = -1
            self.picks_turn = 0
        if self.num_bans == 10:
            self.bans_turn = -1
            self.picks_turn = 1

    def pick_turns(self):
        if self.num_picks == 6:
            self.picks_turn = -1
            self.bans_turn = 1
    
    def get_input(self, team, opp_team, pick=True, player=None):
        if team.is_players_team:
            champion = self.get_player_input()
        else:
            champion = self.get_ai_input(opp_team, pick=pick, player=player)
        
        return champion
    
    def get_player_input(self) -> Champion:
        pass

    def ai_ban_best_champions(self, team) -> None:
        """
        Gets the list of the best champions from the opponent team.
        """
        self.ai_ban_champions.clear()
        champions_id = []

        for player in team.list_players:
            for champion in player.champions:
                champions_id.append(champion)
        
        for ch_id in champions_id:
            champion = ChampionGenerator().get_champion_by_id(ch_id["id"], self.champion_list)
            self.ai_ban_champions.append(champion)

        for champion in self.ai_ban_champions:
            if champion not in self.champion_list:
                self.ai_ban_champions.remove(champion)

        # If the list is empty, chooses a random champion from the list
        if not self.ai_ban_champions:
            self.ai_ban_champions.append(random.choice(self.champion_list))

    def get_ai_pick_champions(self, player) -> None:
        self.ai_pick_champions.clear()
        champions_id = []
        for champion_id in player.champions:
            champions_id.append(champion_id)
        
        for ch_id in champions_id:
            champion = ChampionGenerator().get_champion_by_id(ch_id["id"], self.champion_list)
            self.ai_pick_champions.append(champion)
        
        for champion in self.ai_pick_champions:
            if champion not in self.champion_list:
                self.ai_pick_champions.remove(champion)
        
        # If the list is empty, chooses a random champion from the list
        if not self.ai_pick_champions:
            self.ai_pick_champions.append(random.choice(self.champion_list))

    def get_ai_input(self, opp_team, pick=True, player=None) -> Champion:
        """
        Gets the AI pick or ban.
        """
        if pick is True:
            champion = self.get_ai_pick_input(player)
        else:
            champion = self.get_ai_ban_input(opp_team)
        
        return champion

    def get_ai_pick_input(self, player) -> Champion:
        if self.ai_pick_champions is None:
            self.ai_pick_champions = []

        self.get_ai_pick_champions(player)

        champion = random.choice(self.ai_pick_champions)
        
        return champion
    
    def get_ai_ban_input(self, opp_team) -> Champion:
        """
        Returns the champions that the AI is going to ban, based on the best champions on the opponent's team player pool.

        Still a naive implementation, should consider best players above everything.
        """
        if self.ai_ban_champions is None:
            self.ai_ban_champions = []
            self.ai_ban_best_champions(opp_team)
        
        champion = random.choice(self.ai_ban_champions)

        return champion
    
    def picks_bans(self):
        self.set_up_player_picks()

        while self.num_picks < 10:
            player = self.picks_order[0]

            self.switch_ban_turn()

            if self.ban_turns != -1:
                self.ban_turns()
            
            if self.picks_turn != -1:
                self.switch_pick_turn(player)
