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

from esm.ui.layouts.controllers.controllerinterface import IController
from esm.ui.layouts.game.game_dashboard import GameDashboardLayout


class GameDashboardController(IController):
    def __init__(self, controller):
        super().__init__(controller)
        self.layout = GameDashboardLayout(self)

    def update(self, event, values, make_screen):
        if event == "dashboard_cancel_btn":
            make_screen("game_dashboard_screen", "main_screen")
