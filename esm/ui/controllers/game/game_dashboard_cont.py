#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2024  Pedrenrique G. Guimarães
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

from typing import Optional

from esm.core.esmcore import ESMCore
from esm.core.esports.moba.mobateam import MobaTeam
from esm.ui.controllers.controllerinterface import IController
from esm.ui.igamecontroller import IGameController
from esm.ui.layouts.game.game_dashboard import GameDashboardLayout


class GameDashboardController(IController):
    def __init__(self, controller: IGameController, core: ESMCore):
        self.controller = controller
        self.core = core
        self.layout = GameDashboardLayout()
        self.team_name: Optional[MobaTeam] = None
        # TODO: rewrite this class

    def update(self, event, values, make_screen):
        pass
