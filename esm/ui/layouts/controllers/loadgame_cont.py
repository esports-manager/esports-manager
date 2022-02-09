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
import os
from .controllerinterface import IController
from ..loadgame import LoadGameLayout
from esm.core.load_game import LoadGame
from esm.core.game_manager import GameManager


class LoadGameController(IController):
    def __init__(self, controller):
        super().__init__(controller)
        self.layout = LoadGameLayout(self)
        self.load_game: LoadGame = LoadGame()
        self.load_files = None
        self.filename = None
        self.default_value = ["No save games encountered"]

    def load_save_files(self):
        self.load_files = self.load_game.get_load_game_files(".cbor")

    def update(self, event, values, make_screen):
        if self.controller.get_gui_element("load_game_screen").visible:
            if self.load_files is None:
                self.load_save_files()

            if event == "load_game_cancel_btn":
                make_screen("load_game_screen", "main_screen")

            if self.load_files:
                self.controller.update_gui_element("load_game_listbox", values=self.load_files)
            else:
                self.controller.update_gui_element("load_game_listbox", values=self.default_value)

            if event == "load_game_listbox":
                self.filename = values["load_game_listbox"][0]
                print(self.filename)

            if event == "load_game_btn":
                if self.filename not in [[], self.default_value, None]:
                    filename = os.path.join(self.controller.settings.save_file_dir, self.filename)
                    gamestate = self.load_game.load_game_state(filename)
                    self.controller.game_manager = GameManager.get_game_manager(gamestate, self.controller.settings)
                    self.controller.manager = self.controller.game_manager.manager
                    make_screen("load_game_screen", "game_dashboard_screen")
                else:
                    self.controller.get_gui_information_window(
                        "Select a file",
                        "Select a save game file"
                    )
        else:
            self.load_files = None
            self.filename = None
