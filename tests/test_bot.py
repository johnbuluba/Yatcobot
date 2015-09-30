import unittest
import logging
from unittest.mock import patch, MagicMock

from yatcobot.bot import Yatcobot, Config, PeriodicScheduler


logging.disable(logging.ERROR)


class TestBot(unittest.TestCase):

    @patch('yatcobot.bot.TwitterClient')
    @patch('yatcobot.bot.IgnoreList')
    @patch('yatcobot.bot.Config')
    def setUp(self, config_mock, ignore_list_mock, client_mock):
        self.config = config_mock
        self.client = client_mock
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

    def test_remove_oldest_follow_empty(self):
        follows = [x for x in range(Config.max_follows - 1)]
        self.bot.client.get_friends_ids.return_value = follows
        self.bot.remove_oldest_follow()
        self.assertFalse(self.bot.client.unfollow.called)

    def test_remove_oldest_follow_full(self):
        follows = [x for x in range(Config.max_follows + 1)]
        self.bot.client.get_friends_ids.return_value = follows
        self.bot.remove_oldest_follow()
        self.bot.client.unfollow.assert_called_with(Config.max_follows)

    def test_update_blocked_users(self):
        users = [x for x in range(10)]
        self.bot.ignore_list = list()
        self.bot.client.get_blocks.return_value = users
        self.bot.update_blocked_users()
        self.assertEqual(users, self.bot.ignore_list)

    def test_run(self):
        mock_scheduler = MagicMock(PeriodicScheduler)
        self.bot.scheduler = mock_scheduler
        self.bot.run()
        self.assertEqual(mock_scheduler.enter.call_count, 4)
        self.assertEqual(mock_scheduler.enter_random.call_count, 1)
        self.assertTrue(mock_scheduler.run.called)