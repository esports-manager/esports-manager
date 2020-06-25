import unittest

from src.core.match_live import get_match_obj_test


class MainTest(unittest.TestCase):
    def setUp(self) -> None:
        self.match = get_match_obj_test()

    def test_get_match(self) -> None:
        self.assertIsNotNone(self.match)


if __name__ == '__main__':
    unittest.main()
