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
from esm.core.utils import load_list_from_file


class LoadGame:
    def __init__(self, filename):
        self.filename = filename

    def check_game_file(self):
        """
        Checks the integrity of the game file. If there are missing keywords, it's a corrupted savefile, and the game cannot be loaded.
        """
        pass
    
    def load_game_file(self):
        self.check_game_file()
        
