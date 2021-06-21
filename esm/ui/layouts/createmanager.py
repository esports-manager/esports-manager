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


class CreateManagerLayout(LayoutInterface):
    def __init__(self, controller):
        super().__init__(controller)
        self.lay = self.layout()
        self.col = self.column()

    def column(self):
        return sg.Column(
            self.lay,
            key="create_manager_screen",
            visible=False,
            element_justification="center",
        )

    def layout(self):
        label_pad = (0, 5)

        nationalities = ["Brazil", "Korea", "United States"]

        labels = [
            [esm_form_text("Name: ", pad=label_pad)],
            [esm_form_text("Nickname: ", pad=label_pad)],
            [esm_form_text("Birthday: ", pad=label_pad)],
            [esm_form_text("Nationality: ", pad=label_pad)],
        ]
        
        controls = [
            [esm_input_text("", key="create_manager_name")],
            [esm_input_text("", key="create_manager_nickname")],
            [esm_input_text("", key="create_manager_birthday")],
            [esm_input_combo(nationalities, default_value=nationalities[0], key="create_manager_nationality")],
        ]

        return [
            [esm_title_text("Create your manager")],
            [sg.Column(labels, element_justification="right"),
             sg.Column(controls, element_justification="left")],
            [esm_button("Create", key="create_manager_create_btn"),
             esm_button("Cancel", key="create_manager_cancel_btn")],
        ]

    def update(self, event, values, make_screen):
        if event == "create_manager_cancel_btn":
            make_screen("create_manager_screen", "new_game_screen")

        if event == "create_manager_create_btn":
            if (
                    values["create_manager_name"] != ""
                    and values["create_manager_nickname"] != ""
                    and values["create_manager_birthday"] != ""
            ):
                print("Go to team selection screen")
            else:
                print("This can't be empty!")
