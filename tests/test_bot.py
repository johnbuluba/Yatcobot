import unittest
import logging
from unittest.mock import patch, MagicMock

from yatcobot.bot import Yatcobot, Config


logging.disable(logging.ERROR)


class TestBot(unittest.TestCase):

    @patch('yatcobot.bot.TwitterClient')
    @patch('yatcobot.bot.IgnoreList')
    @patch('yatcobot.bot.Config')
    def setUp(self, config_mock, ignore_list_mock, client_mock):
        self.config = config_mock
        self.bot = Yatcobot('test', 'test')

    def test_get_original_tweet_no_retweet(self):
        post = {'id': 1000}
        original = self.bot._get_original_tweet(post)
        self.assertEqual(post, original)

    def test_get_original_tweet_retweet(self):
        post = {'id': 1000, 'retweeted_status': {'id': 1001}}
        original = self.bot._get_original_tweet(post)
        self.assertEqual(post['retweeted_status'], original)

    def test_clear_queue_empty(self):
        Config.max_queue = 60
        self.bot.post_list = MagicMock()
        self.bot.post_list.__len__.return_value = 0
        self.bot.clear_queue()
        self.assertFalse(self.bot.post_list.popitem.called)

    def test_clear_queue_full(self):
        self.config.max_queue = 60
        self.bot.post_list = MagicMock()
        self.bot.post_list.__len__.return_value = self.config.max_queue + 1

        self.bot.clear_queue()
        self.assertTrue(self.bot.post_list.popitem.called)
        self.bot.post_list.popitem.assert_called_with(last=False)