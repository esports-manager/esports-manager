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
from abc import ABC, abstractmethod


class IGameController(ABC):
    @abstractmethod
    def get_gui_element(self, element):
        pass

    @abstractmethod
    def make_screen_visible(self, inv_screen, vis_screen):
        pass

    @abstractmethod
    def update_element_on_screen(self, element, **kwargs):
        pass

    @abstractmethod
    def write_event_value(self, firs_message, second_message):
        pass

    @abstractmethod
    def update_progress_bar(self, key, value):
        pass

    @abstractmethod
    def get_gui_information_window(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_gui_confirmation_window(self, *args, **kwargs):
        pass

    @abstractmethod
    def print_error(self, e):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def update(self):
        pass
