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

from ..gui_components import *
from ...resources.generator.generate_players import MobaPlayerGenerator

from .layoutinterface import ILayout


class GameDashboardLayout(ILayout):
    def __init__(self, controller):
        super().__init__(controller)
        self.lay = self.layout()
        self.col = self.column()

    def column(self) -> sg.Column:
        return sg.Column(
            self.lay,
            key="game_dashboard_screen",
            visible=False,
            element_justification="center",
        )

    def layout(self) -> list:
        """
        Defines the main game dashboard screen.
        """
        
        return [
            [esm_title_text("TEAMNAME123456\n")],
            [esm_title_text("Testing screen")],
            [esm_button("Cancel", key="dashboard_cancel_btn")]
        ]

    def update(self, *args, **kwargs) -> None:
        self.controller.update(*args, **kwargs)
