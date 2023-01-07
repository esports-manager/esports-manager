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

        value = [["                                ", "   "]]

        team_table = [
            [esm_form_text("Teams", size=16)],
            [esm_table(values=value, display_row_numbers=True, num_rows=20, headings=headings_teams,
                       key="teamselect_team_table", enable_events=True), ],
        ]

        player_table = [
            [esm_form_text("Players", size=16)],
            [esm_table(values=[["   ", "Select your team", "   "]], num_rows=20, headings=headings_players,
                       key="teamselect_players_table", enable_events=True), ],
        ]

        return [
            [esm_title_text("Select your team\n")],
            [esm_form_text('')],  # line break
            # TODO: IMPLEMENT REGIONS COMBO BOX
            # [esm_input_combo(values=regions, key="teamselect_regions_combo")],
            [sg.Column(team_table, justification='center', element_justification='center'),
             sg.Column(player_table, justification='center', element_justification='center')],
            [esm_button("Select", key="teamselect_select_btn"), esm_button("Cancel", key="teamselect_cancel_btn")],
        ]

    def update(self, *args, **kwargs) -> None:
        self.controller.update(*args, **kwargs)
