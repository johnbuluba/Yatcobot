import builtins
import unittest
import logging
from unittest.mock import patch, mock_open

from yatcobot.bot import Config


logging.disable(logging.ERROR)


class TestConfig(unittest.TestCase):

    config_data='''{"search_queries":["test"],"follow_keywords":["test"],"fav_keywords":["test"],"consumer_key":"test","consumer_secret":"test","access_token_key":"test","access_token_secret":"test","retweet_interval":1,"retweet_random_margin":1,"scan_interval":1,"clear_queue_interval":1,"max_queue":1,"rate_limit_update_interval":1,"min_ratelimit_percent":1,"blocked_users_update_interval":1,"max_follows":1}'''

    def test_load(self):

        #Mock open to return the confi_data from file
        with patch.object(builtins,'open',mock_open(read_data=self.config_data)) as m:
            Config.load("test")

        self.assertEqual(Config.search_queries, ["test"])
        self.assertEqual(Config.follow_keywords,["test"])
        self.assertEqual(Config.scan_interval, 1)
        self.assertEqual(Config.retweet_interval, 1)
        self.assertEqual(Config.rate_limit_update_interval, 1)
        self.assertEqual(Config.min_ratelimit_percent, 1)
        self.assertEqual(Config.clear_queue_interval, 1)
        self.assertEqual(Config.max_queue, 1)
        self.assertEqual(Config.blocked_users_update_interval, 1)
        self.assertEqual(Config.max_follows, 1)
        self.assertEqual(Config.consumer_key, "test")
        self.assertEqual(Config.consumer_secret, "test")
        self.assertEqual(Config.access_token_key, "test")
        self.assertEqual(Config.access_token_secret, "test")

    def test_save_tokens(self):
        with patch.object(builtins,'open',mock_open(read_data=self.config_data)) as m:
            Config.save_user_tokens("test", "new_token", "new_secret")
            handle = m()
            handle.write.assert_any_call('"new_token"')
            handle.write.assert_any_call('"new_secret"')

