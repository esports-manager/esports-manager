#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020  Pedrenrique G. Guimarães
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

from src.core.esports.moba.team import Team
from src.resources.utils import write_to_json, get_list_from_file


class TeamGeneratorError(Exception):
    pass


class TeamGenerator:
    def __init__(self, nationality: str = None, amount: int = 1, players: list = None, organized: bool = False):
        self.name = None
        self.nationality = nationality
        self.logo = None
        self.team_id = None
        self.file_name = 'teams.json'
        self.teams = []
        self.teams_dict = []
        self.team_dict = None
        self.team_obj = None
        self.player_list = players
        self.roster = None
        self.names = get_list_from_file('team_names.txt')
        self.amount = amount
        self.organized = organized

    def generate_id(self):
        self.team_id = uuid.uuid4()

    def generate_name(self):
        self.name = random.choice(self.names)
        self.names.remove(self.name)

    def generate_logo(self):
        pass

    def get_roster(self):
        self.roster = []
        if self.player_list is not None:
            lane = 0
            for i in range(5):
                if self.organized is False:
                    player = random.choice(self.player_list)
                else:
                    for player_ in self.player_list:
                        x = player_.mult.index(max(player_.mult))
                        if x == lane:
                            player = player_
                            lane += 1
                            break
                    else:
                        raise TeamGeneratorError('No player found!')

                self.roster.append(player)
                self.player_list.remove(player)
        else:
            raise TeamGeneratorError('List of players is not valid!')

    def get_roster_ids(self):
        r_ids = []
        if self.roster is not None and self.roster != []:
            for player in self.roster:
                r_ids.append(player.player_id.int)
        else:
            raise TeamGeneratorError('Player roster is invalid!')

        return r_ids

    def get_dictionary(self):
        self.team_dict = {'id': self.team_id.int,
                          'name': self.name,
                          'roster': self.get_roster_ids()}

    def get_object(self):
        self.team_obj = Team(self.team_id, self.name, self.roster)

    def get_nationality(self):
        pass

    def generate_team(self):
        self.generate_id()
        self.generate_name()
        self.get_roster()
        self.get_dictionary()
        self.get_object()
        self.teams.append(self.team_obj)
        self.teams_dict.append(self.team_dict)

    def generate_teams(self):
        for i in range(self.amount):
            self.generate_team()

    def generate_file(self):
        write_to_json(self.teams_dict, self.file_name)


if __name__ == '__main__':
    from src.resources.generator.generate_players import MobaPlayerGenerator

    amount = 100
    teams = int(amount / 5)
    player = MobaPlayerGenerator(lane=1)
    player.generate_players(amount=amount)
    team = TeamGenerator(amount=teams, players=player.players, organized=True)
    team.generate_teams()
    for team_ in team.teams:
        for player in team_.list_players:
            print(player.get_lane())
