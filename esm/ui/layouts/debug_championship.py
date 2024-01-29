#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2024  Pedrenrique G. Guimarães
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


class DebugChampionshipLayout(ILayout):
    def __init__(self):
        self.lay = self.layout()
        self.col = self.column()

    def column(self) -> sg.Column:
        return sg.Column(
            self.lay,
            key="debug_championship_screen",
            visible=False,
            element_justification="center",
        )

    def layout(self) -> list:
        headings_championship_table = [
            "Team Name",
            "Skill",
            "Wins",
            "Losses",
            "Points",
        ]

        headings_matches = [
            "Blue Team",
            "Red Team",
            "Winning Team",
        ]

        championship_table_column = [
            [esm_form_text("Debug Championhsip")],
            [
                esm_table(
                    [["TEAM1NAME123456789", "000", "00", "00", "0000"]],
                    num_rows=20,
                    display_row_numbers=True,
                    headings=headings_championship_table,
                    key="debug_championship_table",
                ),
            ],
        ]

        matches_column = [
            [
                esm_form_text("Matches", key="debug_championship_matches"),
            ],
            [
                esm_table(
                    [["TEAM1NAME123456789", "TEAM2NAME123456789", "00"]],
                    num_rows=20,
                    display_row_numbers=True,
                    headings=headings_matches,
                    key="debug_matches_table",
                ),
            ],
        ]

        return [
            [esm_title_text("Debug Championship")],
            [
                sg.Column(
                    layout=championship_table_column, element_justification="center"
                ),
                sg.Column(layout=matches_column, element_justification="center"),
            ],
            [
                esm_button("Start Championship", key="debug_startchampionship_btn"),
                esm_button("Cancel", key="debug_championshipcancel_btn"),
            ],
        ]
