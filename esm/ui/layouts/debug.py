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

from ..gui_components import *
from .layoutinterface import ILayout


class DebugLayout(ILayout):
    def __init__(self, controller):
        super().__init__(controller)
        self.lay = self.layout()
        self.col = self.column()

    def column(self) -> sg.Column:
        return sg.Column(
            self.lay,
            key="debug_game_mode_screen",
            visible=False,
            element_justification="center",
        )

    def layout(self) -> list:
        """
        Defines the Debug Game Mode screen. This screen shows the Debug game options.
        """

        button_pad = (0, 10)
        button_size = (20, 2)

        return [
            [esm_title_text("Choose your debug mode")],
            [
                esm_button(
                    "Debug Match",
                    key="debug_match_btn",
                    pad=button_pad,
                    size=button_size,
                )
            ],
            [
                esm_button(
                    "Debug Pick Team",
                    key="debug_pickteam_btn",
                    pad=button_pad,
                    size=button_size,
                )
            ],
            [
                esm_button(
                    "Debug Picks Bans",
                    key="debug_picksbans_btn",
                    pad=button_pad,
                    size=button_size,
                )
            ],
            [
                esm_button(
                    "Debug Championship",
                    key="debug_championship_btn",
                    pad=button_pad,
                    size=button_size,
                )
            ],
            [
                esm_button(
                    "Match Tester",
                    key="debug_matchtester_btn",
                    pad=button_pad,
                    size=button_size,
                )
            ],
            [
                esm_button(
                    "Cancel",
                    key="debug_cancelmain_btn",
                    pad=button_pad,
                    size=button_size,
                )
            ],
        ]

    def update(self, *args, **kwargs) -> None:
        self.controller.update(*args, **kwargs)
