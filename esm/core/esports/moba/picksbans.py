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
from .team import Team
from .player import MobaPlayer
from .champion import Champion

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

    def pick(self, player: MobaPlayer, champion: Champion) -> None:
        player.champion = champion
        self.champion_list.remove(champion)
    
    def ban(self, team: Team, champion: Champion) -> None:
        team.bans = champion
        self.champion_list.remove(champion)

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
        if self.bans_turn == 0:
            champion = self.get_input(self.team1)
            self.ban(self.team1, champion)
            self.bans_turn = 1
        elif self.bans_turn == 1:
            champion = self.get_input(self.team2)
            self.ban(self.team2, champion)
            self.bans_turn = 0
        
        self.num_bans += 1

    def switch_pick_turn(self):
        if self.picks_turn == 0:
            champion = self.get_input(self.team1)
        elif self.picks_turn == 1:
            champion = self.get_input(self.team2)
    
    def ban_turns(self):
        if self.num_bans == 6 or self.num_bans == 10:
            self.bans_turn = -1
            self.picks_turn = 0

    def get_input(self, team):
        champion = None
        
        if team.is_players_team:
            champion = self.get_player_input()
        else:
            champion = self.get_ai_input()
        
        return champion
    
    def get_player_input(self):
        pass

    def get_ai_input(self):
        pass
    
    def picks_bans(self):
        self.set_up_player_picks()
        
        while True:
            self.switch_ban_turn()

            self.ban_turns()
            
            self.switch_pick_turn()