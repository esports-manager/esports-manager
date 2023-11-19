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

from esm.ui.layouts.mainscreen import MainScreenLayout
from .controllerinterface import IController


class MainScreenController(IController):
    def __init__(self):
        self.layout = MainScreenLayout()

    def update(self, event, values, make_screen):
        if event == "main_debug_btn":
            make_screen("main_screen", "debug_game_mode_screen")

        elif event == "main_newgame_btn":
            make_screen("main_screen", "new_game_screen")

        elif event == "main_loadgame_btn":
            make_screen("main_screen", "load_game_screen")

        elif event == "main_settings_btn":
            make_screen("main_screen", "settings_screen")
