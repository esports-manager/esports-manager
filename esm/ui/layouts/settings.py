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

from .layoutinterface import ILayout
from ..gui_components import *


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

        label_pad = (0, 7)
        labels_file_pad = (0, 9)
        controls_file_pad = (6, 8)
        labels_inputs = [
            [esm_form_text("Language:", pad=label_pad)],
            [esm_form_text("Font scale:", pad=label_pad)],
            [esm_form_text("Amount of players to generate:", pad=label_pad)],
        ]

        labels_files = [
            [esm_form_text("Root directory:", pad=labels_file_pad)],
            [esm_form_text("Resources directory:", pad=labels_file_pad)],
            [esm_form_text("Database directory:", pad=labels_file_pad)],
            [esm_form_text("Saves directory:", pad=labels_file_pad)],
            [esm_form_text("Champions file:", pad=labels_file_pad)],
            [esm_form_text("Players file:", pad=labels_file_pad)],
            [esm_form_text("Teams file:", pad=labels_file_pad)],
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
            [esm_input_text("1", size=size_elements, key="settings_fontsize_input", pad=(3, 5))],
            [
                esm_input_text("50", key="settings_amount_input", size=size_elements),
                esm_button(
                    "Generate",
                    font=(default_font, default_font_size),
                    key="settings_generate_btn",
                ),
            ],
            [esm_checkbox("Enable autosave: ", default=True, key="settings_enable_autosave")],
        ]

        controls_files = [
            [
                esm_input_text('', size=size_elements, key="settings_root_dir", pad=controls_file_pad),
                sg.FileBrowse(target="settings_root_dir", font=(default_font, default_font_size)),
            ],
            [
                esm_input_text('', size=size_elements, key="settings_res_dir", pad=controls_file_pad),
                sg.FileBrowse(target="settings_res_dir", font=(default_font, default_font_size)),
            ],
            [
                esm_input_text('', size=size_elements, key="settings_db_dir", pad=controls_file_pad),
                sg.FileBrowse(target="settings_db_dir", font=(default_font, default_font_size)),
            ],
            [
                esm_input_text('', size=size_elements, key="settings_saves_dir", pad=controls_file_pad),
                sg.FileBrowse(target="settings_saves_dir", font=(default_font, default_font_size)),
            ],
            [
                esm_input_text('', size=size_elements, key="settings_ch_file", pad=controls_file_pad),
                sg.FileBrowse(target="settings_ch_file", font=(default_font, default_font_size)),
            ],
            [
                esm_input_text('', size=size_elements, key="settings_pl_file", pad=controls_file_pad),
                sg.FileBrowse(target="settings_pl_file", font=(default_font, default_font_size)),
            ],
            [
                esm_input_text('', size=size_elements, key="settings_t_file", pad=controls_file_pad),
                sg.FileBrowse(target="settings_t_file", font=(default_font, default_font_size)),
            ],
        ]

        return [
            [esm_title_text("Settings")],
            [
                sg.Column(labels_inputs, element_justification="right"),
                sg.Column(controls, element_justification="left"),
            ],
            [esm_form_text("Warning: Generating players will replace the current champions, players and teams file!")],
            [
                sg.Column(labels_files, element_justification="right"),
                sg.Column(controls_files, element_justification="left"),
            ],
            [esm_form_text("", pad=(0, 80))],
            [
                esm_button("Apply", key="settings_apply_btn"),
                esm_button("Cancel", key="settings_cancel_btn"),
            ],
        ]

    def update(self, *args, **kwargs) -> None:
        self.controller.update(*args, **kwargs)
