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
from esm.core.esmcore import ESMCore
from esm.core.utils import get_nations, load_list_from_file
from esm.ui.igamecontroller import IGameController
from esm.ui.layouts.newgame import NewGameLayout

from .controllerinterface import IController


class NewGameController(IController):
    def __init__(self, controller: IGameController, core: ESMCore):
        self.core = core
        self.controller = controller
        self.layout = NewGameLayout()
        self.nationalities = None

    def load_nationalities(self):
        if self.nationalities is None:
            names = load_list_from_file(self.core.settings.names_file)
            self.nationalities = get_nations(names)
            self.controller.get_gui_element("create_manager_nationality").update(
                values=self.nationalities
            )

    def update(self, event, values, make_screen):
        if self.controller.get_gui_element("new_game_screen").visible:
            self.load_nationalities()

            if event == "ng_cancel_btn":
                make_screen("new_game_screen", "main_screen")

            elif event == "ng_next_btn":
                if len(values["ng_gamename_input"]) > 20:
                    self.controller.get_gui_information_window(
                        "Game name not allowed! It must be a maximum of 20 characters long!",
                        "Game name not allowed!",
                    )
                elif len(values["create_manager_name"]) > 50:
                    self.controller.get_gui_information_window(
                        "Manager name not allowed! Manager name must be a maximum of 50 characters long!",
                        "Manager name not allowed!",
                    )
                elif len(values["create_manager_nickname"]) > 20:
                    self.controller.get_gui_information_window(
                        "Manager nickname not allowed! Manager nickname must be a maximum of 20 characters long!",
                        "Manager nickname not allowed!",
                    )
                elif (
                    values["ng_gamename_input"] != ""
                    and values["create_manager_name"] != ""
                    and values["create_manager_nickname"] != ""
                    and values["create_manager_display_calendar"] != ""
                ):
                    if values["new_game_checkbox"]:
                        self.core.db.generate_moba_files()

                    make_screen("new_game_screen", "team_select_screen")
                else:
                    self.controller.get_gui_information_window(
                        "You must fill all the fields before proceeding!",
                        "Fill all the fields!",
                    )
