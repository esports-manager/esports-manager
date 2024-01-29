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

from esm.core.esmcore import ESMCore
from esm.core.esports.manager import Manager
from esm.ui.igamecontroller import IGameController
from esm.ui.layouts.teamselect import TeamSelectLayout

from .controllerinterface import IController


class TeamSelectControllerError(Exception):
    pass


class TeamSelectController(IController):
    def __init__(self, controller: IGameController, core: ESMCore):
        self.controller = controller
        self.core = core
        self.layout = TeamSelectLayout()
        self.teams = None

    def get_teams(self):
        try:
            self.core.check_files()
        except FileNotFoundError:
            self.teams = self.core.db.load_moba_teams()

    def get_team_list(self):
        return [[team.name, team.get_team_overall()] for team in self.teams.teams]

    def get_player_list(self, team):
        data = []
        if not self.teams.teams:
            return ["    ", "Select your team", "       "]

        for player in self.teams.teams[team[0]].list_players:
            player.get_default_lane()
            data.append([player.lane.name, player.nick_name, player.skill])

        return data

    def select_team(self, values, make_screen):
        if values["teamselect_team_table"]:
            team_index = values["teamselect_team_table"][0]
            manager = Manager(
                values["create_manager_name"],
                values["create_manager_display_calendar"],
                self.teams.teams[team_index],
                True,
                50,
            )
            self.teams.teams[team_index].is_players_team = True
            # Probably here we should delete the old window and create a new one with new layouts
            # self.create_game_manager(
            #             manager,
            #             values["ng_gamename_input"],
            #             values["new_game_esport"],
            #             values["new_game_season"],
            #             values["ng_gamename_input"],
            #         )
            make_screen("team_select_screen", "game_dashboard_screen")
        else:
            self.controller.get_gui_information_window(
                "You must select a team before proceeding!", title="Select a team!"
            )

    def cancel_teamselect(self, make_screen):
        self.teams = None
        make_screen("team_select_screen", "new_game_screen")

    def update_teams(self, values):
        if self.teams is None:
            self.get_teams()
            self.controller.update_element_on_screen(
                "teamselect_team_table", values=self.get_team_list()
            )

        if values["teamselect_team_table"]:
            self.controller.update_element_on_screen(
                "teamselect_players_table",
                values=self.get_player_list(values["teamselect_team_table"]),
            )

    def update(self, event, values, make_screen):
        if self.controller.get_gui_element("team_select_screen").visible:
            self.update_teams(values)

            # Click the Cancel button
            if event == "teamselect_cancel_btn":
                self.cancel_teamselect(make_screen)

            if event == "teamselect_select_btn":
                self.select_team(values, make_screen)
        else:
            self.teams = None
