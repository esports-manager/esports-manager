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

from .controllerinterface import IController
from ..settings import SettingsLayout


class SettingsController(IController):
    def __init__(self, controller):
        super().__init__(controller)
        self.layout = SettingsLayout(self)

    def generate_all_data(self) -> None:
        self.controller.generate_all_data()

    def update(self, event, values, make_screen):
        if event == "settings_cancel_btn":
            make_screen("settings_screen", "main_screen")

        elif event == "settings_generate_btn":
            try:
                value = int(values["settings_amount_input"])
            except ValueError:
                self.controller.amount_players = 400
                self.controller.update_amount(400)
            else:
                self.controller.amount_players = value
            self.controller.generate_all_data()
