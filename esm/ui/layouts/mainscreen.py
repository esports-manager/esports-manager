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

import os

from esm.definitions import DEBUG, RES_DIR

from ..gui_components import *
from .layoutinterface import ILayout


class MainScreenLayout(ILayout):
    def __init__(self):
        self.lay = self.layout()
        self.col = self.column()

    def column(self) -> sg.Column:
        return sg.Column(self.lay, key="main_screen", element_justification="center")

    def layout(self) -> list:
        """
        Defines the main screen. This screen shows the initial options to play a new game, load game,
        use the Database Editor, or exit the game.
        """
        logo_path = os.path.join(RES_DIR, "images", "logo", "esportsmanager.png")

        button_pad = (0, 10)
        button_size = (20, 2)

        if DEBUG:
            debug_button = [
                esm_button(
                    "Debug Game Mode",
                    key="main_debug_btn",
                    pad=button_pad,
                    size=button_size,
                )
            ]
        else:
            debug_button = []

        return [
            [sg.Image(logo_path, pad=(50, 0))],
            debug_button,
            [
                esm_button(
                    "New Game", key="main_newgame_btn", pad=button_pad, size=button_size
                )
            ],
            [
                esm_button(
                    "Load Game",
                    key="main_loadgame_btn",
                    pad=button_pad,
                    size=button_size,
                )
            ],
            [
                esm_button(
                    "Settings",
                    key="main_settings_btn",
                    pad=button_pad,
                    size=button_size,
                )
            ],
            [esm_button("Exit", key="main_exit_btn", pad=button_pad, size=button_size)],
        ]
