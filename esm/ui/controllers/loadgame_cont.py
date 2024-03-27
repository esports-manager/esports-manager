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
import os

from esm.core.esmcore import ESMCore
from esm.core.save_load.load_game import LoadGame
from esm.ui.igamecontroller import IGameController
from esm.ui.layouts.loadgame import LoadGameLayout

from .controllerinterface import IController


class LoadGameController(IController):
    def __init__(self, controller: IGameController, core: ESMCore):
        self.controller = controller
        self.core = core
        self.layout = LoadGameLayout()
        self.load_game: LoadGame = LoadGame(self.core.settings.save_file_dir)
        self.load_files = None
        self.filename = None
        self.default_value = ["No save games encountered"]

    def get_save_files(self):
        self.load_files = self.load_game.get_load_game_files(".cbor")
        if not self.load_files:
            self.load_files = self.default_value

    def update(self, event, values, make_screen):
        if self.controller.get_gui_element("load_game_screen").visible:
            if self.load_files is None:
                self.get_save_files()

            if event == "load_game_cancel_btn":
                make_screen("load_game_screen", "main_screen")

            if self.load_files:
                self.controller.update_element_on_screen(
                    "load_game_listbox", values=self.load_files
                )
            else:
                self.controller.update_element_on_screen(
                    "load_game_listbox", values=self.default_value
                )

            if event == "load_game_listbox":
                self.filename = values["load_game_listbox"][0]

            if event == "load_game_btn":
                if self.filename not in [[], self.default_value, None]:
                    filename = os.path.join(
                        self.core.settings.save_file_dir, self.filename
                    )
                    self.core.game_session.load_game(filename)
                    make_screen("load_game_screen", "game_dashboard_screen")
                else:
                    self.controller.get_gui_information_window(
                        "Select a file", "Select a save game file"
                    )
        else:
            self.load_files = None
            self.filename = None
