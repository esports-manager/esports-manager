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


class MatchTesterLayout(ILayout):
    def __init__(self, controller):
        super().__init__(controller)
        self.lay = self.layout()
        self.col = self.column()

    def column(self) -> sg.Column:
        return sg.Column(
            self.lay,
            key="match_tester_screen",
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
                esm_form_text("Team1DebugMatch", key="match_tester_team1name"),
                esm_form_text("0000", key="match_tester_team1skill"),
            ],
            [esm_table(headings, headings=headings, key="match_tester_team1table")],
        ]

        team2_column = [
            [
                esm_form_text("Team2DebugMatch", key="match_tester_team2name"),
                esm_form_text("0000", key="match_tester_team2skill"),
            ],
            [esm_table(headings, headings=headings, key="match_tester_team2table")],
        ]

        return [
            [esm_title_text("Match Tester")],
            [esm_form_text("Match tester provides a way to test matches efficiently!")],
            [
                esm_form_text("Amount of matches: "),
                esm_input_text("1000", key="match_tester_amount_of_matches"),
            ],
            [
                sg.Column(layout=team1_column, element_justification="center"),
                sg.Column(layout=team2_column, element_justification="center"),
            ],
            [esm_output()],
            [
                esm_button("Start Test", key="match_tester_startmatch_btn"),
                esm_button("New Teams", key="match_tester_newteams_btn"),
                esm_button("Cancel", key="match_tester_cancel_btn"),
            ],
        ]

    def update(self, *args, **kwargs) -> None:
        self.controller.update(*args, **kwargs)
