import logging
import os
import unittest
from collections import OrderedDict

import confuse

from tests.helper_func import load_fixture_config
from yatcobot.bot import Config

logging.disable(logging.ERROR)


class TestConfig(unittest.TestCase):

    def test_load_without_user_config(self):
        with self.assertRaises(confuse.ConfigTypeError):
            Config.load()

    def test_load_values(self):
        load_fixture_config()

        # Global settings
        self.assertEqual(Config.get_config().consumer_key, "test")
        self.assertEqual(Config.get_config().consumer_secret, "test")
        self.assertEqual(Config.get_config().access_token_key, "test")
        self.assertEqual(Config.get_config().access_token_secret, "test")
        self.assertEqual(Config.get_config().min_ratelimit_percent, 10)

        # Search settings
        self.assertIsInstance(Config.get_config().search.queries, list)
        self.assertEqual(len(Config.get_config().search.queries), 3)
        self.assertEqual(Config.get_config().search.queries[0], "test1")
        self.assertEqual(Config.get_config().search.queries[1], "test2")
        self.assertIsInstance(Config.get_config().search.queries[2], OrderedDict)
        self.assertIn("test3", Config.get_config().search.queries[2])
        self.assertIn("lang", Config.get_config().search.queries[2]["test3"])
        self.assertEqual(Config.get_config().search.queries[2]["test3"]["lang"], "el")
        self.assertEqual(Config.get_config().search.max_queue, 100)
        self.assertEqual(Config.get_config().search.max_quote_depth, 20)
        self.assertEqual(Config.get_config().search.min_quote_similarity, 0.5)
        self.assertEqual(Config.get_config().search.priority_keywords, ["ps4", "pc"])

        # Actions
        self.assertEqual(Config.get_config().actions.follow.enabled, True)
        self.assertEqual(Config.get_config().actions.follow.keywords, ["follow", "follower"])
        self.assertEqual(Config.get_config().actions.follow.max_following, 1950)
        self.assertEqual(Config.get_config().actions.favorite.enabled, True)
        self.assertEqual(Config.get_config().actions.favorite.keywords, ["fav", "favorite"])

        # Scheduler
        self.assertEqual(Config.get_config().scheduler.search_interval, 5400)
        self.assertEqual(Config.get_config().scheduler.retweet_interval, 600)
        self.assertEqual(Config.get_config().scheduler.retweet_random_margin, 60)
        self.assertEqual(Config.get_config().scheduler.blocked_users_update_interval, 300)
        self.assertEqual(Config.get_config().scheduler.clear_queue_interval, 60)
        self.assertEqual(Config.get_config().scheduler.rate_limit_update_interval, 60)
        self.assertEqual(Config.get_config().scheduler.check_mentions_interval, 600)

        # Notifiers
        self.assertEqual(Config.get_config().notifiers.pushbullet.enabled, False)
        self.assertEqual(Config.get_config().notifiers.pushbullet.token, "test")
