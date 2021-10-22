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
import os

from ..gui_components import *
from esm.resources.utils import find_file
from .layoutinterface import ILayout
from esm.definitions import DB_DIR, CHAMPIONS_FILE, PLAYERS_FILE, TEAMS_FILE


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
            ch_file = find_file(CHAMPIONS_FILE)
            pl_file = find_file(PLAYERS_FILE)
            t_file = find_file(TEAMS_FILE)
        except FileNotFoundError:
            ch_file = os.path.join(DB_DIR, CHAMPIONS_FILE)
            pl_file = os.path.join(DB_DIR, PLAYERS_FILE)
            t_file = os.path.join(DB_DIR, TEAMS_FILE)

        label_pad = (0, 5)
        labels = [
            [esm_form_text("Language:", pad=label_pad)],
            [esm_form_text("Font scale:", pad=label_pad)],
            [esm_form_text("Champions file:", pad=label_pad)],
            [esm_form_text("Players file:", pad=label_pad)],
            [esm_form_text("Teams file:", pad=label_pad)],
            [esm_form_text("Amount of players to generate:", pad=label_pad)],
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
            [esm_form_text("Generating players will replace the current champions, players and teams file!")],
            [esm_form_text("", pad=(0, 175))],
            [
                esm_button("Apply", key="settings_apply_btn"),
                esm_button("Cancel", key="settings_cancel_btn"),
            ],
        ]

    def update(self, *args, **kwargs) -> None:
        self.controller.update(*args, **kwargs)
