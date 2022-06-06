#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2022  Pedrenrique G. Guimarães
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
from typing import Union

from esm.core.esports.moba.team import Team
from core.esports.moba.generator.default_team_names import get_default_team_names
from core.esports.moba.generator.generate_players import MobaPlayerGenerator
from esm.core.utils import write_to_file, load_list_from_file
from esm.definitions import TEAMS_FILE


class TeamGeneratorError(Exception):
    pass


class TeamGenerator:
    def __init__(
            self,
            nationality: str = None,
            amount: int = 1,
            players: list = None,
            organized: bool = True,
            file_name: str = TEAMS_FILE,
    ):
        self.name = None
        self.nationality = nationality
        self.logo = None
        self.team_id = None
        self.file_name = file_name
        self.teams = []
        self.teams_dict = []
        self.team_dict = None
        self.team_obj = None
        self.player_list = players
        self.roster = None
        self.names = None
        self.amount = amount
        self.organized = organized

    def get_names(self) -> None:
        """
        Gets all available names from the team_names file
        """
        self.names = get_default_team_names()

    def generate_id(self) -> None:
        """
        Generates teams UUID
        """
        self.team_id = uuid.uuid4().int

    def generate_name(self) -> None:
        """
        Chooses a random team name
        """
        self.name = random.choice(self.names)
        self.names.remove(self.name)

    def generate_logo(self) -> None:
        """
        Placeholder for a future logo generator
        """
        pass

    def get_players_list(self) -> None:
        if not self.player_list or self.player_list is None:
            self.player_list = MobaPlayerGenerator()
            try:
                self.player_list.get_players_objects()
                self.player_list = self.player_list.players
            except Exception:
                self.player_list.lane = 0
                self.player_list.generate_players(self.amount * 5)
                self.player_list = self.player_list.players

    def generate_roster(self) -> None:
        """
        Generates a roster.
        If the self.organized attribute is set to True, it is going to generate teams with players that are specialists
        at their lanes.
        Otherwise, it selects random players, regardless of their lane specialty.
        """
        self.roster = []
        self.get_players_list()

        lane = 0
        for _ in range(5):
            if self.organized is False:
                player = random.choice(self.player_list)
            else:
                for player_ in self.player_list:
                    if player_.get_best_lane() == lane:
                        player = player_
                        lane += 1
                        break
                else:
                    raise TeamGeneratorError("No player found!")

            self.roster.append(player)
            self.player_list.remove(player)

    def get_roster_ids(self) -> list:
        """
        Gets the IDs of each player to save on the dictionary
        """
        if self.roster is None or self.roster == []:
            raise TeamGeneratorError("Player roster is invalid!")

        return [player.player_id for player in self.roster]

    def get_dictionary(self) -> None:
        """
        Generates the team dictionary
        """
        self.team_dict = {
            "id": self.team_id,
            "name": self.name,
            "roster": self.get_roster_ids(),
        }

    def get_object(self) -> None:
        """
        Generates the team object
        """
        self.team_obj = Team(self.team_id, self.name, self.roster)

    def get_nationality(self) -> None:
        """
        Placeholder for team nationality
        TODO: leagues and cups should also be considered
        """
        pass

    def generate_team(self) -> None:
        """
        Runs the team generation routine
        """
        if self.names is None:
            self.get_names()

        # Prevents IndexError
        if len(self.names) < self.amount:
            self.amount = len(self.names)

        self.generate_id()
        self.generate_name()
        self.generate_roster()
        self.get_dictionary()
        self.get_object()
        self.teams.append(self.team_obj)
        self.teams_dict.append(self.team_dict)

    def generate_teams(self) -> None:
        """
        Generates a "self.amount" of teams
        """
        for _ in range(self.amount):
            self.generate_team()

    def get_teams_dict(self) -> None:
        """
        Retrieves teams list based on the teams file
        """
        if self.teams_dict:
            self.teams_dict.clear()
        self.get_players_list()
        self.teams_dict = load_list_from_file(self.file_name)

    def get_roster(self, team) -> list:
        """
        Gets the roster based on the player's ID
        """
        self.roster = []
        if self.player_list is not None:
            for roster_id in team["roster"]:
                for player in self.player_list:
                    if player.player_id == roster_id:
                        self.roster.append(player)
                        break

        return self.roster

    def get_teams_objects(self) -> None:
        """
        Retrieves champions objects based on teams list dict
        """
        self.teams = []
        if not self.teams_dict:
            self.get_teams_dict()
        self.get_players_list()
        for team in self.teams_dict:
            self.team_id = team["id"]
            self.name = team["name"]
            self.get_roster(team)
            self.get_object()
            self.teams.append(self.team_obj)

    def get_from_data_file(self, data: list, only_dict: bool = False):
        self.teams_dict = data.copy()
        if not only_dict:
            self.teams = [Team.get_from_dict(team) for team in self.teams_dict]

    def get_team_from_id(self, team_id: Union[int, uuid.UUID]):
        for team in self.teams:
            if team.team_id == team_id:
                return team

        raise ValueError("Team ID not found!")

    def generate_file(
            self,
    ) -> None:
        """
        Generates the teams file
        """
        write_to_file(self.teams_dict, self.file_name)
