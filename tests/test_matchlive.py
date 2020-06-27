import unittest

from src.core.match_live import get_match_obj_test
from src.core.match import Match


class MatchLiveTest(unittest.TestCase):
    def setUp(self) -> None:
        self.match = get_match_obj_test()

    def test_event(self):
        self.assertEqual(None, None)


if __name__ == '__main__':
    unittest.main()
