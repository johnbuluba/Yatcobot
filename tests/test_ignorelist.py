import builtins
import logging
import unittest
from unittest.mock import patch, mock_open

from yatcobot.ignorelist import IgnoreList

logging.disable(logging.ERROR)


class TestIgnoreList(unittest.TestCase):

    def test_load_file(self):
        data = '0\n1\n2'
        with patch.object(builtins, 'open', mock_open(read_data=data)) as m:
            ignorelist = IgnoreList("test")

        self.assertEqual(len(ignorelist), 3)
        for x in range(3):
            self.assertIn(x, ignorelist)

    def test_append(self):
        with patch.object(builtins, 'open', mock_open()) as m:
            ignorelist = IgnoreList("test")
            ignorelist.append(1)
            file_handler = m.return_value.__enter__.return_value
            file_handler.write.assert_called_with('1\n')

            self.assertIn(1, ignorelist)

    def test_append_same_values(self):
        data = '0\n0\n0'
        with patch.object(builtins, 'open', mock_open(read_data=data)) as m:
            ignorelist = IgnoreList("test")

        self.assertEqual(len(ignorelist), 1)
        self.assertIn(0, ignorelist)
