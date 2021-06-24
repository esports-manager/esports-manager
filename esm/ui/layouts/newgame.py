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

from .layoutinterface import ILayout


class NewGameLayout(ILayout):
    def __init__(self, controller):
        super().__init__(controller)
        self.lay = self.layout()
        self.col = self.column()

    def column(self) -> sg.Column:
        return sg.Column(
            self.lay,
            key="new_game_screen",
            visible=False,
            element_justification="center",
        )

    def layout(self) -> list:
        """
        Defines the new game screen.
        """

        label_pad = (0, 5)
        esports = ["MOBA", "RTS", "FPS"]
        seasons = ["2020"]
        nationalities = ["Brazil", "Korea", "United States"]

        labels = [
            [esm_form_text("Game Name:", pad=label_pad)],
            [esm_form_text("Season: ", pad=label_pad)],
            [esm_form_text("eSport: ", pad=label_pad)],
            [esm_form_text("")],
        ]

        labels_create_manager = [
            [esm_form_text("Name: ", pad=label_pad)],
            [esm_form_text("Nickname: ", pad=label_pad)],
            [esm_form_text("Birthday: ", pad=label_pad)],
            [esm_form_text("Nationality: ", pad=label_pad)],
        ]

        inputs = [
            [esm_input_text("Game1", key="ng_gamename_input")],
            [esm_input_combo(seasons, default_value=seasons[0], key="new_game_season")],
            [esm_input_combo(esports, default_value=esports[0], key="new_game_esport")],
            [esm_checkbox("Generate new database", key="new_game_checkbox")],
        ]

        inputs_create_manager = [
            [esm_input_text("", key="create_manager_name")],
            [esm_input_text("", key="create_manager_nickname")],
            [esm_input_text("", key="create_manager_birthday")],
            [esm_input_combo(nationalities, default_value=nationalities[0], key="create_manager_nationality")],
        ]

        return [
            [esm_title_text("New Game\n")],
            [
                sg.Column(labels, element_justification="right"),
                sg.Column(inputs, element_justification="left"),
            ],
            [esm_form_text("")],
            [esm_title_text("Create Manager\n", font=(bold_font, "15"))],
            [
                sg.Column(labels_create_manager, element_justification="right"),
                sg.Column(inputs_create_manager, element_justification="left"),
            ],
            [
                esm_button("Create Game", key="ng_creategame_btn"),
                esm_button("Cancel", key="ng_cancel_btn"),
            ],
        ]

    def update(self, event, values, make_screen) -> None:
        if event == "ng_cancel_btn":
            make_screen("new_game_screen", "main_screen")

        elif event == "ng_creategame_btn":
            if (
                    values["create_manager_name"] != ""
                    and values["create_manager_nickname"] != ""
                    and values["create_manager_birthday"] != ""
            ):
                if values["new_game_checkbox"]:
                    print("Generate new database")
                
                make_screen("new_game_screen", "team_select_screen")
            else:
                print("This can't be empty!")
