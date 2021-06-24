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
from esm.resources.utils import find_file
from .layoutinterface import ILayout


class SettingsLayout(ILayout):
    def __init__(self, controller):
        super().__init__(controller)
        self.lay = self.layout()
        self.col = self.column()

    def column(self) -> sg.Column:
        return sg.Column(
            self.lay,
            key="settings_screen",
            visible=False,
            element_justification="center",
        )

    def layout(self) -> list:
        size_elements = (45, 2)

        languages = ["English", "Portuguese"]

        try:
            ch_file = find_file("champions.json")
            pl_file = find_file("players.json")
            t_file = find_file("teams.json")
        except FileNotFoundError:
            ch_file = "champions.json"
            pl_file = "players.json"
            t_file = "teams.json"

        labels = [
            [esm_form_text("Language:")],
            [esm_form_text("Font scale:")],
            [esm_form_text("Champions file:")],
            [esm_form_text("Players file:")],
            [esm_form_text("Teams file:")],
            [esm_form_text("Generate new files:")],
        ]

        controls = [
            # TODO: Replace with supported i18n
            [
                esm_input_combo(
                    languages,
                    default_value=languages[0],
                    size=size_elements,
                    key="settings_languages_inpcombo",
                )
            ],
            [esm_input_text("1", size=size_elements, key="settings_fontsize_input")],
            [
                esm_input_text(ch_file, size=size_elements, key="settings_ch_file"),
                sg.FileBrowse(target="settings_ch_file"),
            ],
            [
                esm_input_text(pl_file, size=size_elements, key="settings_pl_file"),
                sg.FileBrowse(target="settings_pl_file"),
            ],
            [
                esm_input_text(t_file, size=size_elements, key="settings_t_file"),
                sg.FileBrowse(target="settings_t_file"),
            ],
            [
                esm_input_text("400", key="settings_amount_input", size=size_elements),
                esm_button(
                    "Generate",
                    font=(default_font, default_font_size),
                    key="settings_generate_btn",
                ),
            ],
        ]

        return [
            [esm_title_text("Settings")],
            [
                sg.Column(labels, element_justification="right"),
                sg.Column(controls, element_justification="left"),
            ],
            [
                esm_button("Apply", key="settings_apply_btn"),
                esm_button("Cancel", key="settings_cancel_btn"),
            ],
        ]

    def update(self, event, values, make_screen) -> None:
        if event == "settings_cancel_btn":
            make_screen("settings_screen", "main_screen")

        elif event == "settings_generate_btn":
            try:
                value = int(values["settings_amount_input"])
            except ValueError:
                self.controller.amount_players = 400
                self.controller.update_amount(400)
            else:
                self.controller.amount_players = value
            self.controller.generate_all_data()
