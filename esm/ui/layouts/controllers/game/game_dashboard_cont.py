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

from esm.ui.layouts.controllers.controllerinterface import IController
from esm.ui.layouts.game.game_dashboard import GameDashboardLayout
from esm.core.game_manager import GameManager


class GameDashboardController(IController):
    def __init__(self, controller):
        super().__init__(controller)
        self.layout = GameDashboardLayout(self)
        self.game_manager: GameManager = self.controller.game_manager

    def update(self, event, values, make_screen):
        if self.controller.get_gui_element("game_dashboard_screen").visible:
            if self.game_manager is None:
                self.game_manager = self.controller.game_manager
            if event == "dashboard_cancel_btn":
                make_screen("game_dashboard_screen", "main_screen")

            if event == "game_dashboard_save":
                self.game_manager.save_game()