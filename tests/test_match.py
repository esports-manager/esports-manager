import unittest

from src.core.match_live import get_match_obj_test
from src.core.match import Match


class MainTest(unittest.TestCase):
    def setUp(self) -> None:
        self.match = get_match_obj_test()

    def test_get_match(self) -> None:
        self.assertIsNotNone(self.match)
        self.assertIsInstance(self.match, Match)


if __name__ == '__main__':
    unittest.main()
