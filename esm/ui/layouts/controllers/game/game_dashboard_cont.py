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
import uuid

from esm.core.esports.manager import Manager
from esm.core.esports.moba.team import Team
from esm.core.game_manager import GameManager
from esm.ui.layouts.controllers.controllerinterface import IController
from esm.ui.layouts.game.game_dashboard import GameDashboardLayout


class GameDashboardController(IController):
    def __init__(self, controller):
        super().__init__(controller)
        self.layout = GameDashboardLayout(self)
        self.game_manager: GameManager = None
        self.current_manager: Manager = None
        self.team_name: Team = None

    def get_manager_details(self):
        self.current_manager = self.game_manager.manager

    def get_team_name(self):
        self.game_manager.get_gamestate_for_generators()
        if isinstance(self.game_manager.manager.team, Team):
            self.team_name = self.game_manager.manager.team
        if isinstance(self.game_manager.manager.team, (int, uuid.UUID)):
            self.team_name = self.game_manager.teams.get_team_from_id(self.game_manager.manager.team)

    def update(self, event, values, make_screen):
        if not self.controller.get_gui_element("game_dashboard_screen").visible:
            self.game_manager = None
            self.team_name = None
            self.current_manager = None
        else:
            if self.game_manager is None:
                self.game_manager = self.controller.game_manager

            if self.current_manager is None and self.game_manager is not None:
                self.get_manager_details()

            if self.team_name is None and self.game_manager is not None:
                self.get_team_name()
                team_name = self.controller.get_gui_element("game_dashboard_teamname")
                team_name.set_size((len(self.team_name.name) * 2, None))
                self.controller.update_gui_element("game_dashboard_teamname", value=self.team_name.name)

            if event == "game_dashboard_save":
                if self.game_manager.save is None:
                    self.game_manager.create_save_game()

                if self.game_manager.check_if_save_file_exists(self.game_manager.save.filename):
                    ovrw = self.controller.get_gui_confirmation_window(
                        "There is an existing file with the same name, do you want to overwrite it?",
                        title="Overwrite Save File",
                    )
                    if ovrw == "OK":
                        self.game_manager.save_game()
                        self.controller.get_gui_information_window("Game was successfully saved!", "Saved!")
                else:
                    self.game_manager.save_game()
                    self.controller.get_gui_information_window("Game was successfully saved!", "Saved!")
