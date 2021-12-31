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
from ..settings import SettingsLayout


class SettingsController(IController):
    def __init__(self, controller):
        super().__init__(controller)
        self.layout = SettingsLayout(self)
        self._amount_players = 50

    @property
    def amount_players(self) -> int:
        return self._amount_players

    @amount_players.setter
    def amount_players(self, amount):
        self.controller.core.amount_players = amount
        self._amount_players = amount

    def generate_all_data(self) -> None:
        self.controller.generate_all_data()

    def update_amount(self, amount):
        self.controller.update_gui_element("settings_amount_input", value=amount)

    def update(self, event, values, make_screen):
        if event == "settings_cancel_btn":
            make_screen("settings_screen", "main_screen")

        elif event == "settings_generate_btn":
            try:
                value = int(values["settings_amount_input"])
                self.controller.core.check_player_amount()
            except ValueError as e:
                self.controller.get_gui_information_window(
                    e,
                    'Error in number of players!'
                )
                self.amount_players = 50
                self.update_amount(50)
            else:
                self.controller.amount_players = value
            finally:
                self.controller.generate_all_data()
                self.update_amount(self.amount_players)
