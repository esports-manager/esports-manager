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


class PickTeamLayout(ILayout):
    def __init__(self, controller):
        super().__init__(controller)
        self.lay = self.layout()
        self.col = self.column()

    def column(self) -> sg.Column:
        return sg.Column(
            self.lay,
            key="debug_pickteam_screen",
            visible=False,
            element_justification="center",
        )

    def layout(self) -> list:
        team_headings = ["Team Name", "Skill"]
        player_headings = ["Lane", "Nickname", "Nationality", "Skill"]

        team_list_frame = [
            [esm_form_text("Team:")],
            [
                esm_table(
                    values=[["", ""]],
                    key="debug_pick_team_table",
                    headings=team_headings,
                    enable_events=True,
                )
            ],
        ]

        player_list_frame = [
            [esm_form_text("Players:")],
            [
                esm_table(
                    values=[["", "Select a team", "", ""]],
                    key="debug_pick_player_table",
                    headings=player_headings,
                    enable_events=True,
                )
            ],
        ]

        return [
            [esm_title_text("Pick your team")],
            [
                sg.Column(team_list_frame, element_justification="center"),
                sg.Column(player_list_frame, element_justification="center"),
            ],
            [
                esm_button("Confirm", key="debug_confirmteam_btn"),
                esm_button("Cancel", key="debug_cancelteam_btn"),
            ],
        ]

    def update(self, event, values, make_screen) -> None:
        if event == "debug_cancelteam_btn":
            make_screen("debug_pickteam_screen", "debug_game_mode_screen")
