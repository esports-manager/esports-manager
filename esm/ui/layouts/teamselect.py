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


class TeamSelectLayout(ILayout):
    def __init__(self, controller):
        super().__init__(controller)
        self.lay = self.layout()
        self.col = self.column()

    def column(self) -> sg.Column:
        return sg.Column(
            self.lay,
            key="team_select_screen",
            visible=False,
            element_justification="center",
        )

    
    def layout(self) -> list:
        headings_teams = [
            "Name",
            "Overall"
        ]

        headings_players = [
            "Lane",
            "Nick name",
            "Skill"
        ]

        value = [["TEAMNAMES1234567890", "100"]]

        return [
            [esm_title_text("Select your team\n")],
            # TODO: IMPLEMENT REGIONS COMBO BOX
            # [esm_input_combo(values=regions, key="teamselect_regions_combo")],
            [
                esm_table(values=value, headings=headings_teams, key="teamselect_team_table", enable_events=True),
                esm_table(values=[["   ", "Select your team", "   "]], headings=headings_players, key="teamselect_players_table", enable_events=True),
            ],
            [esm_button("Select", key="teamselect_select_btn"), esm_button("Cancel", key="teamselect_cancel_btn")],
        ]

    def update(self, event, values, make_screen) -> None:
        # Click the Select
        if event == "teamselect_select_btn":
            if values["teamselect_team_table"] is not None:
                pass

        # Click the Cancel button
        elif event == "teamselect_cancel_btn":
            make_screen("team_select_screen", "new_game_screen")