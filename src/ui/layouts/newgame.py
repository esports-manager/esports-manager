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

import PySimpleGUI as sg
from ..gui_components import *

from .layoutinterface import LayoutInterface


class NewGameLayout(LayoutInterface):
    def __init__(self, controller):
        super().__init__(controller)
        self.lay = self.layout()
        self.col = self.column()

    def column(self):
        return sg.Column(
            self.lay,
            key="new_game_screen",
            visible=False,
            element_justification="center",
        )

    def layout(self):
        """
        Defines the new game screen.
        """

        label_pad = (0, 5)
        size_element = (29, 1)

        labels = [
            [esm_form_text("Game Name:", pad=label_pad)],
        ]

        inputs = [[esm_input_text(key="ng_gamename_input", size=size_element)]]

        return [
            [esm_title_text("New Game")],
            [
                sg.Column(labels, element_justification="left"),
                sg.Column(inputs, element_justification="left"),
            ],
            [
                esm_button("Create Game", key="ng_creategame_btn"),
                esm_button("Cancel", key="ng_cancel_btn"),
            ],
        ]

    def update(self, event, values, make_screen):
        if event == "ng_cancel_btn":
            make_screen("new_game_screen", "main_screen")
