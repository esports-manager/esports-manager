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


class DebugMatchLayout(ILayout):
    def __init__(self, controller):
        super().__init__(controller)
        self.lay = self.layout()
        self.col = self.column()

    def column(self) -> sg.Column:
        return sg.Column(
            self.lay,
            key="debug_match_screen",
            visible=False,
            element_justification="center",
        )

    def layout(self) -> list:
        headings = [
            "Lane",
            "Player Name",
            "Kills",
            "Deaths",
            "Assists",
            "Champion",
            "Skill",
        ]

        team1_column = [
            [
                esm_form_text("Team1DebugMatch", key="debug_team1name"),
                esm_form_text("0000", key="debug_team1skill"),
            ],
            [esm_form_text("0.0000", key="debug_team1winprob")],
            [esm_table(headings, headings=headings, key="debug_team1table")],
            [
                esm_form_text("Towers: "),
                esm_form_text(
                    {"top": 3, "mid": 3, "bot": 3, "base": 2}, key="debug_team1towers"
                ),
            ],
            [
                esm_form_text("Inhibitors: "),
                esm_form_text({"top": 1, "mid": 1, "bot": 1}, key="debug_team1inhibs"),
            ],
        ]

        team2_column = [
            [
                esm_form_text("Team2DebugMatch", key="debug_team2name"),
                esm_form_text("0000", key="debug_team2skill"),
            ],
            [esm_form_text("0.0000", key="debug_team2winprob")],
            [esm_table(headings, headings=headings, key="debug_team2table")],
            [
                esm_form_text("Towers: "),
                esm_form_text(
                    {"top": 3, "mid": 3, "bot": 3, "base": 2}, key="debug_team2towers"
                ),
            ],
            [
                esm_form_text("Inhibitors: "),
                esm_form_text({"top": 1, "mid": 1, "bot": 1}, key="debug_team2inhibs"),
            ],
        ]

        return [
            [esm_title_text("Debug Match")],
            [
                sg.Column(layout=team1_column, element_justification="center"),
                sg.Column(layout=team2_column, element_justification="center"),
            ],
            [sg.ProgressBar(100, size=(80, 20), border_width=0, key="debug_winprob")],
            [
                esm_form_text("Current match time: "),
                esm_form_text("500.00", key="debug_match_current_time"),
            ],
            [esm_output()],
            [esm_checkbox("Simulate step-by-step", key="debug_simulate_checkbox")],
            [
                esm_button("Start Match", key="debug_startmatch_btn"),
                esm_button("New Teams", key="debug_newteams_btn"),
                esm_button("Reset Match", key="debug_resetmatch_btn"),
                esm_button("Cancel", key="debug_cancel_btn"),
            ],
        ]

    def update(self, *args, **kwargs) -> None:  
        self.controller.update(*args, **kwargs)
