import unittest

from src.core.match_live import get_match_obj_test


class MatchLiveTest(unittest.TestCase):
    def setUp(self) -> None:
        self.match = get_match_obj_test()


if __name__ == '__main__':
    unittest.main()
