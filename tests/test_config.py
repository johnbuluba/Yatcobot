import builtins
import unittest
import logging
from unittest.mock import patch, mock_open

from yatcobot.main import Config


logging.disable(logging.ERROR)


class TestConfig(unittest.TestCase):

    config_data='''{"search_queries":["test"],"follow_keywords":["test"],"fav_keywords":["test"],"scan_update_time":1,"retweet_update_time":1,"rate_limit_update_time":1,"min_ratelimit":1,"min_ratelimit_retweet":1,"min_ratelimit_search":1,"clear_queue_time":1,"min_posts_queue":1,"blocked_users_update_time":1,"max_follows":1,"consumer_key":"test","consumer_secret":"test","access_token_key":"test","access_token_secret":"test"}'''

    def test_load(self):

        #Mock open to return the confi_data from file
        with patch.object(builtins,'open',mock_open(read_data=self.config_data)) as m:
            Config.load("test")

        self.assertEqual(Config.search_queries, ["test"])
        self.assertEqual(Config.follow_keywords,["test"])
        self.assertEqual(Config.scan_update_time, 1)
        self.assertEqual(Config.retweet_update_time, 1)
        self.assertEqual(Config.rate_limit_update_time, 1)
        self.assertEqual(Config.min_ratelimit, 1)
        self.assertEqual(Config.min_ratelimit_search, 1)
        self.assertEqual(Config.clear_queue_time, 1)
        self.assertEqual(Config.min_posts_queue, 1)
        self.assertEqual(Config.blocked_users_update_time, 1)
        self.assertEqual(Config.max_follows, 1)
        self.assertEqual(Config.consumer_key, "test")
        self.assertEqual(Config.consumer_secret, "test")
        self.assertEqual(Config.access_token_key, "test")
        self.assertEqual(Config.access_token_secret, "test")
