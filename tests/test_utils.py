#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020  Pedrenrique G. Guimarães
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
import unittest

from src.resources.utils import find_file
from src.definitions import ROOT_DIR


class UtilsTest(unittest.TestCase):
    def test_find_invalid_file(self):
        with self.assertRaises(FileNotFoundError):
            find_file('anythingelse.txt')
    
    def test_find_file(self):
        file = find_file('get_names.py')
        self.assertIsNotNone(file)
        self.assertIn('get_names.py', file)

    def test_find_image(self):
        image = find_file('esportsmanagertrophy.png')
        dir_n = os.path.join(ROOT_DIR, 'resources', 'images', 'logo', 'esportsmanagertrophy.png')
        self.assertEqual(dir_n, image)
        self.assertIsNotNone(image)


if __name__ == '__main__':
    unittest.main()
