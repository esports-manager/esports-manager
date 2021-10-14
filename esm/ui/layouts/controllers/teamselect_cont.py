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

from .controllerinterface import IController
from ..teamselect import TeamSelectLayout
from esm.resources.generator.generate_teams import TeamGenerator
from esm.resources.generator.generate_players import MobaPlayerGenerator
from esm.core.esports.moba.manager import Manager


class TeamSelectControllerError(Exception):
    pass


class TeamSelectController(IController):
    def __init__(self, controller):
        super().__init__(controller)
        self.layout = TeamSelectLayout(self)
        self.teams = None

    def get_teams(self):
        self.controller.check_files()
        self.teams = self.controller.core.teams
        self.controller.core.get_teams()
    
    def get_team_list(self):
        return [
            [team.name, team.get_team_overall()] for team in self.teams.teams
        ]
    
    def get_player_list(self, team):
        data = []
        for player in self.teams.teams[team[0]].list_players:
            player.get_default_lane()
            data.append([player.lane.name, player.nick_name, player.skill])
        
        return data
        
    def update(self, event, values, make_screen):
        if self.controller.view.gui.window["team_select_screen"].visible is True:
            if self.teams is None:
                self.get_teams()
                self.controller.view.gui.window["teamselect_team_table"].update(values=self.get_team_list())

            if values["teamselect_team_table"]:
                self.controller.view.gui.window["teamselect_players_table"].update(values=self.get_player_list(values["teamselect_team_table"]))

            # Click the Cancel button
            if event == "teamselect_cancel_btn":
                make_screen("team_select_screen", "new_game_screen")
            
            if event == "teamselect_next_btn":
                team = values["teamselect_team_table"][0]
                manager = Manager(
                    values["create_manager_name"],
                    values["create_manager_display_calendar"],
                    self.teams.teams[team],
                    True,
                    50
                )
                self.teams.teams[team].is_players_team = True
                self.controller.manager = manager
                # make_screen("team_select_screen", "game_screen")
        else:
            self.teams = None
