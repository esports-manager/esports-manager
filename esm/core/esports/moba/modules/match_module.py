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

from esm.core.esports.moba.match import Match
from esm.core.esports.moba.match_live import MatchLive

class MatchModule:
    @staticmethod
    def initialize_new_match(team1, team2):
        return Match(
            uuid.uuid4().int,
            uuid.uuid4().int,
            team1,
            team2
        )

    @staticmethod
    def initialize_new_match_live(
        match,
        show_commentary=True,
        match_speed=1,
        simulate=True,
        ban_per_team=5,
        difficulty_level=1,
        is_player_match=False
    ):
        return MatchLive(
            match,
            show_commentary,
            match_speed,
            simulate,
            ban_per_team=ban_per_team,
            difficulty_level=difficulty_level,
            is_player_match=is_player_match
        )
    
    def initialize_random_debug_match(self, teams) -> MatchLive:
        team1 = random.choice(teams)
        teams.remove(team1)
        team2 = random.choice(teams)
        teams.remove(team2)

        match = self.initialize_new_match(team1, team2)
        return self.initialize_new_match_live(match)

    @staticmethod
    def get_match(match_id, db_module, team_module) -> Match:
        match_dict = db_module.get_dict(match_id)
        
        team1 = team_module.get_team(match_dict["team1_id"])
        team2 = team_module.get_team(match_dict["team2_id"])
        
        champ_id = match_dict["ch_id"]
        
        match = Match(
            match_id,
            champ_id,
            team1,
            team2
        )
        
        if match_dict["victorious_team"] == team1.team_id:
            match.victorious_team = team1
        elif match_dict["victorious_team"] == team2.team_id:
            match.victorious_team = team2
        
        return match
    
    def get_match_live(self, match_id, db_module, team_module) -> MatchLive:
        match = self.get_match(match_id, db_module, team_module)
        return MatchLive(match)
