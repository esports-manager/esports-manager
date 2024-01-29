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


class PicksBansLayout(ILayout):
    def __init__(self):
        self.lay = self.layout()
        self.col = self.column()

    def column(self) -> sg.Column:
        return sg.Column(
            self.lay,
            key="debug_picks_bans_screen",
            visible=False,
            element_justification="center",
        )

    def layout(self) -> list:
        team_headings = ["Lane", "Nickname", "Skill", "Champion", "Ch. Skill"]

        champion_headings = ["Name", "Skill", "Pl. Skill", "Status"]

        values = [
            "LANE",
            "PLAYERNICKNAME123456",
            "0000",
            "CHAMPIONNAME",
            "0000",
        ]

        col_team1 = [
            [
                esm_form_text("Team1WholeName", key="pickban_team1_label"),
                esm_form_text("(Your team)"),
            ],
            [
                esm_table(
                    values=[values],
                    headings=team_headings,
                    key="pickban_team1_table",
                    num_rows=5,
                    enable_events=True,
                )
            ],
            [esm_form_text("Bans:")],
            [esm_multiline(key="pickban_team1_bans", size=(60, 3))],
            [esm_form_text("Team2WholeName", key="pickban_team2_label")],
            [
                esm_table(
                    values=[values],
                    headings=team_headings,
                    key="pickban_team2_table",
                    num_rows=5,
                    enable_events=True,
                )
            ],
            [esm_form_text("Bans:")],
            [esm_multiline(key="pickban_team2_bans", size=(60, 3))],
        ]

        col_champion = [
            [esm_form_text("Champions")],
            [
                esm_table(
                    values=[["CHAMPIONWHOLENAME", "0000", "0000", "Not picked"]],
                    headings=champion_headings,
                    key="pickban_champion_table",
                    num_rows=30,
                    enable_events=True,
                )
            ],
        ]

        return [
            [esm_title_text("Picks and Bans")],
            [sg.Column(col_team1), sg.Column(col_champion)],
            [
                esm_button("Pick", key="pickban_pick_btn"),
                esm_button("Cancel", key="pickban_cancel_btn"),
            ],
        ]
