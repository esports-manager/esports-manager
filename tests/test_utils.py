import unittest

from src.resources.utils import *


class UtilsTest(unittest.TestCase):
    def test_get_current_folder(self):
        file = get_current_folder()
        self.assertEqual(os.path.dirname(os.path.abspath(__file__)), file)


if __name__ == '__main__':
    unittest.main()
