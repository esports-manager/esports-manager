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
