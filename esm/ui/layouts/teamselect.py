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


class TeamSelectLayout(LayoutInterface):
    def __init__(self, controller):
        super().__init__(controller)
        self.lay = self.layout()
        self.col = self.column()

    def column(self):
        return sg.Column(
            self.lay,
            key="team_select_screen",
            visible=False,
            element_justification="center",
        )

    def layout(self):
        headings = [
            "Lane",
            "Player Name",
            "Kills",
            "Deaths",
            "Assists",
            "Champion",
            "Skill",
        ]

        teams = [
            [
                esm_form_text("Team1DebugMatch", key="debug_team1name"),
                esm_form_text("0000", key="debug_team1skill"),
            ],
            [esm_form_text("0.0000", key="debug_team1winprob")],
            [esm_table(headings, headings=headings, key="debug_team1table")],
            [
                esm_form_text("Team 1 Towers: "),
                esm_form_text(
                    {"top": 3, "mid": 3, "bot": 3, "base": 2}, key="debug_team1towers"
                ),
            ],
            [
                esm_form_text("Team 2 Towers: "),
                esm_form_text({"top": 1, "mid": 1, "bot": 1}, key="debug_team1inhibs"),
            ],
        ]

        players = [
            [
                esm_form_text("Team2DebugMatch", key="debug_team2name"),
                esm_form_text("0000", key="debug_team2skill"),
            ],
            [esm_form_text("0.0000", key="debug_team2winprob")],
            [esm_table(headings, headings=headings, key="debug_team2table")],
            [
                esm_form_text("Team 2 Towers: "),
                esm_form_text(
                    {"top": 3, "mid": 3, "bot": 3, "base": 2}, key="debug_team2towers"
                ),
            ],
            [
                esm_form_text("Team 2 Inhibitors: "),
                esm_form_text({"top": 1, "mid": 1, "bot": 1}, key="debug_team2inhibs"),
            ],
        ]

        return [
            [esm_title_text("Select your team")],
            [
                sg.Column(layout=teams, element_justification="center"),
                sg.Column(layout=players, element_justification="center"),
            ],
            [sg.ProgressBar(100, size=(80, 20), border_width=1, key="debug_winprob")],
            [
                esm_form_text("Current match time: "),
                esm_form_text("500.00", key="debug_match_current_time"),
            ],
            [esm_output()],
            [esm_checkbox("Simulate step-by-step", key="debug_simulate_checkbox")],
            [
                esm_button("Start Game", key="debug_startmatch_btn"),
                esm_button("New Teams", key="debug_newteams_btn"),
                esm_button("Reset Match", key="debug_resetmatch_btn"),
                esm_button("Cancel", key="debug_cancel_btn"),
            ],
        ]

    def update(self, event, values, make_screen):
        team_data = self.controller.team_data
        update_debug_match_info = self.controller.update_debug_match_info

        # Click the Start Match button
        if event == "debug_startmatch_btn":
            self.controller.is_match_running = True
            self.controller.reset_match(self.controller.current_match)
            self.controller.current_match.is_match_over = False
            self.controller.start_match_sim_thread()

        # Click the Cancel button
        if event == "debug_cancel_btn":
            if self.controller.is_match_running:
                self.controller.current_match.is_match_over = True
                self.controller.current_match = None
            make_screen("debug_match_screen", "main_screen")

        # Click the New Teams button
        elif event == "debug_newteams_btn":
            self.controller.check_files()
            self.controller.initialize_random_debug_match()
            data = self.controller.team_data(match_live=self.controller.current_match)
            update_debug_match_info(self.controller.current_match, data)

        # Click the Reset Match button
        elif event == "debug_resetmatch_btn":
            self.controller.reset_match(self.controller.current_match)
            data = self.controller.team_data(match_live=self.controller.current_match)
            update_debug_match_info(self.controller.current_match, data)

        # if self.controller.current_match is not None:
        #     self.controller.current_match.simulate = bool(values['debug_simulate_checkbox'])

        # Check if the match is running to update values on the fly
        if self.controller.is_match_running:
            if (
                self.controller.current_match is not None
                and self.controller.current_match.is_match_over
                and not self.controller.match_thread.is_alive()
            ):
                self.controller.is_match_running = False

            if self.controller.current_match is not None:
                self.controller.current_match.simulate = bool(
                    values["debug_simulate_checkbox"]
                )
                data = team_data(self.controller.current_match)
                update_debug_match_info(self.controller.current_match, data)
