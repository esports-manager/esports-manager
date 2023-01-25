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
from .core import Core
from ..ui.guicontroller import GUIController


class ESMController:
    """
    This class is the Game controller. It initializes the game's modules and game settings.

    This class should also communicate with the UI.
    """

    def __init__(self):
        self.game_manager = None
        self.core = Core()
        self.view = GUIController()

    @property
    def amount_players(self):
        return self.core.amount_players

    @amount_players.setter
    def amount_players(self, value):
        self.core.amount_players = value

    @property
    def settings(self):
        return self.core.settings

    def app(self) -> None:
        self.view.start()
