#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2022  Pedrenrique G. Guimarães
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

from .controllerinterface import IController
from ..newgame import NewGameLayout


class NewGameController(IController):
    def __init__(self, controller):
        super().__init__(controller)
        self.layout = NewGameLayout(self)

    def update(self, event, values, make_screen):
        if event == "ng_cancel_btn":
            make_screen("new_game_screen", "main_screen")

        elif event == "ng_next_btn":
            if (
                    values["create_manager_name"] != ""
                    and values["create_manager_nickname"] != ""
                    and values["create_manager_display_calendar"] != ""
            ):
                if values["new_game_checkbox"]:
                    self.controller.generate_all_data()

                make_screen("new_game_screen", "team_select_screen")
            else:
                self.controller.get_gui_information_window(
                    'You must fill all the fields before proceeding!',
                    'Fill all the fields!'
                )
