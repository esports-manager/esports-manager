import unittest
import pickle
from tempfile import NamedTemporaryFile
from src.resources.utils import load_list_from_json


class FileTest(unittest.TestCase):
    def test_serialization(self):
        data = load_list_from_json('players.json')
        with NamedTemporaryFile(delete=False, mode='wb') as temp_file:
            pickle.dump(data, temp_file)
            with open(temp_file.name, 'rb') as fp:
                file_data = pickle.load(fp)
                self.assertEqual(data, file_data)
                self.assertIsInstance(data, list)


if __name__ == '__main__':
    unittest.main()
