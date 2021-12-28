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

from .layoutinterface import ILayout
from ..gui_components import *


class LoadGameLayout(ILayout):
    def __init__(self, controller):
        super().__init__(controller)
        self.lay = self.layout()
        self.col = self.column()

    def column(self) -> sg.Column:
        return sg.Column(
            self.lay,
            key="load_game_screen",
            visible=False,
            element_justification="center",
        )

    def layout(self):
        saved_games = [
            "No save games encountered",
        ]

        size_btn = (10, 1)

        return [
            [esm_title_text("Load Game")],
            [esm_form_text("Saved Games:")],
            [
                esm_listbox(
                    saved_games,
                    size=(50, 20),
                    key="load_game_listbox",
                    enable_events=True,
                )
            ],
            [
                esm_button("Load Game", key="load_game_btn", size=size_btn),
                esm_button("Cancel", key="load_game_cancel_btn", size=size_btn),
            ],
        ]

    def update(self, *args, **kwargs):
        self.controller.update(*args, **kwargs)
