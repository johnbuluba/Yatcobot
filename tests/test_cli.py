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
        yatcobot.cli.TwitterConfig = MagicMock()

    def test_simple_start(self):
        sys.argv = [self.program_name]

        main()

        yatcobot.cli.TwitterConfig.load.assert_called_once_with('config.yaml')
        yatcobot.cli.Yatcobot.assert_called_once_with('ignorelist')
        self.assertTrue(yatcobot.cli.Yatcobot.return_value.run.called)

    def test_simple_select_config(self):
        sys.argv = [self.program_name, '--config', 'test.yaml']

        main()

        yatcobot.cli.TwitterConfig.load.assert_called_once_with('test.yaml')
        yatcobot.cli.Yatcobot.assert_called_once_with('ignorelist')
        self.assertTrue(yatcobot.cli.Yatcobot.return_value.run.called)

    def test_simple_select_ignorelist(self):
        sys.argv = [self.program_name, '--ignore_list', 'test']

        main()

        yatcobot.cli.TwitterConfig.load.assert_called_once_with('config.yaml')
        yatcobot.cli.Yatcobot.assert_called_once_with('test')
        self.assertTrue(yatcobot.cli.Yatcobot.return_value.run.called)

    def test_simple_select_log(self):
        sys.argv = [self.program_name, '--log', 'test']
        yatcobot.cli.create_logger = MagicMock()
        main()

        yatcobot.cli.TwitterConfig.load.assert_called_once_with('config.yaml')
        yatcobot.cli.Yatcobot.assert_called_once_with('ignorelist')
        yatcobot.cli.create_logger.assert_called_once_with(logging.INFO, 'test')
        self.assertTrue(yatcobot.cli.Yatcobot.return_value.run.called)

    def test_simple_debug(self):
        sys.argv = [self.program_name, '--debug']
        yatcobot.cli.create_logger = MagicMock()
        main()

        yatcobot.cli.TwitterConfig.load.assert_called_once_with('config.yaml')
        yatcobot.cli.Yatcobot.assert_called_once_with('ignorelist')
        yatcobot.cli.create_logger.assert_called_once_with(logging.DEBUG, None)
        self.assertTrue(yatcobot.cli.Yatcobot.return_value.run.called)

    def test_email(self):
        sys.argv = [self.program_name, '--test-mail']
        notifier_mock = MagicMock()
        yatcobot.cli.MailNotifier = notifier_mock

        with self.assertRaises(SystemExit):
            main()

        self.assertEqual(notifier_mock.from_config.return_value.test.call_count, 1)
