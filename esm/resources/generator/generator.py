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
from abc import ABC, abstractmethod


class GeneratorInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def get_obj_list(self):
        pass

    @abstractmethod
    def get_dict_list(self):
        pass

    @abstractmethod
    def generate_id(self):
        pass

    @abstractmethod
    def generate_name(self):
        pass

    @abstractmethod
    def generate_obj(self):
        pass

    @abstractmethod
    def generate_dict(self):
        pass

    @abstractmethod
    def generate(self):
        pass

    @abstractmethod
    def generate_file(self):
        pass
