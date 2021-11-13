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
import cbor2
from esm.core.utils import load_list_from_file


class LoadGameError(Exception):
    pass


class LoadGame:
    def __init__(self, folder):
        self.folder = folder

    def check_game_file(self, filename) -> bool:
        """
        Checks the integrity of the game file. If there are missing keywords, it's a corrupted savefile,
        and the game cannot be loaded.
        Returns True if the file is okay, or False otherwise.
        """
        pass
    
    def load_game_file(self, filename):
        if self.check_game_file(filename):
            with open(filename, 'r') as fp:
                return cbor2.load(fp)
        else:
            raise LoadGameError("The save file is corrupted!")

    def get_load_game_files(self) -> list:
        """
        Returns a list of available load game files
        """
        pass
