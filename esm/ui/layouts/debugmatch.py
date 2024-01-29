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

from ..gui_components import *
from .layoutinterface import ILayout


class DebugMatchLayout(ILayout):
    def __init__(self):
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
                esm_form_text("Top tower: 3", key="debug_team1_top_tower"),
                esm_form_text("Mid tower: 3", key="debug_team1_mid_tower"),
                esm_form_text("Bot tower: 3", key="debug_team1_bot_tower"),
                esm_form_text("Base tower: 3", key="debug_team1_base_tower"),
            ],
            [
                esm_form_text("Inhibitors: "),
                esm_form_text("Top inhib: 1", key="debug_team1_top_inhib"),
                esm_form_text("Mid inhib: 1", key="debug_team1_mid_inhib"),
                esm_form_text("Bot inhib: 1", key="debug_team1_bot_inhib"),
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
                esm_form_text("Top tower: 3", key="debug_team2_top_tower"),
                esm_form_text("Mid tower: 3", key="debug_team2_mid_tower"),
                esm_form_text("Bot tower: 3", key="debug_team2_bot_tower"),
                esm_form_text("Base tower: 3", key="debug_team2_base_tower"),
            ],
            [
                esm_form_text("Inhibitors: "),
                esm_form_text("Top inhib: 1", key="debug_team2_top_inhib"),
                esm_form_text("Mid inhib: 1", key="debug_team2_mid_inhib"),
                esm_form_text("Bot inhib: 1", key="debug_team2_bot_inhib"),
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
            [esm_multiline(key="debug_match_output", do_not_clear=True)],
            [esm_checkbox("Simulate step-by-step", key="debug_simulate_checkbox")],
            [
                esm_button("Start Match", key="debug_startmatch_btn"),
                esm_button("New Teams", key="debug_newteams_btn"),
                esm_button("Reset Match", key="debug_resetmatch_btn"),
                esm_button("Cancel", key="debug_cancel_btn"),
            ],
        ]
