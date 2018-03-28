import builtins
import logging
import sys
import unittest
from unittest.mock import MagicMock

import yatcobot.cli
from yatcobot.cli import main

logging.disable(logging.ERROR)


class TestCli(unittest.TestCase):
    program_name = 'yatcobot.py'

    def setUp(self):
        yatcobot.cli.Yatcobot = MagicMock()
        yatcobot.cli.Config = MagicMock()

    def test_simple_start(self):
        sys.argv = [self.program_name]

        main()

        yatcobot.cli.Config.load.assert_called_once_with('config.json')
        yatcobot.cli.Yatcobot.assert_called_once_with('ignorelist')
        self.assertTrue(yatcobot.cli.Yatcobot.return_value.run.called)

    def test_simple_select_config(self):
        sys.argv = [self.program_name, '--config', 'test.json']

        main()

        yatcobot.cli.Config.load.assert_called_once_with('test.json')
        yatcobot.cli.Yatcobot.assert_called_once_with('ignorelist')
        self.assertTrue(yatcobot.cli.Yatcobot.return_value.run.called)

    def test_simple_select_ignorelist(self):
        sys.argv = [self.program_name, '--ignore_list', 'test']

        main()

        yatcobot.cli.Config.load.assert_called_once_with(('config.json'))
        yatcobot.cli.Yatcobot.assert_called_once_with('test')
        self.assertTrue(yatcobot.cli.Yatcobot.return_value.run.called)

    def test_simple_select_log(self):
        sys.argv = [self.program_name, '--log', 'test']
        yatcobot.cli.create_logger = MagicMock()
        main()

        yatcobot.cli.Config.load.assert_called_once_with(('config.json'))
        yatcobot.cli.Yatcobot.assert_called_once_with('ignorelist')
        yatcobot.cli.create_logger.assert_called_once_with(logging.INFO, 'test')
        self.assertTrue(yatcobot.cli.Yatcobot.return_value.run.called)

    def test_simple_debug(self):
        sys.argv = [self.program_name, '--debug']
        yatcobot.cli.create_logger = MagicMock()
        main()

        yatcobot.cli.Config.load.assert_called_once_with(('config.json'))
        yatcobot.cli.Yatcobot.assert_called_once_with('ignorelist')
        yatcobot.cli.create_logger.assert_called_once_with(logging.DEBUG, None)
        self.assertTrue(yatcobot.cli.Yatcobot.return_value.run.called)

    def test_login(self):
        sys.argv = [self.program_name, '--login']
        yatcobot.cli.create_logger = MagicMock()
        yatcobot.cli.get_access_token = MagicMock(return_value={'token': 'test', 'secret': 'test'})
        builtins.input = MagicMock(return_value='y')
        main()

        yatcobot.cli.Config.save_user_tokens.assert_called_once_with('config.json', 'test', 'test')
        yatcobot.cli.Config.load.assert_called_once_with(('config.json'))
        yatcobot.cli.Yatcobot.assert_called_once_with('ignorelist')
        yatcobot.cli.create_logger.assert_called_once_with(logging.INFO, None)
        self.assertTrue(yatcobot.cli.Yatcobot.return_value.run.called)
