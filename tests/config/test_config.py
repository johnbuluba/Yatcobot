import logging
import unittest
from collections import OrderedDict

import confuse

from tests.helper_func import load_fixture_config
from yatcobot.bot import TwitterConfig
from yatcobot.config import NotifiersConfig, Config

logging.disable(logging.ERROR)


class TestConfig(unittest.TestCase):

    def test_load_without_user_config(self):
        Config._valid = None
        with self.assertRaises(confuse.NotFoundError):
            Config.load()

    def test_access_before_load(self):
        Config._valid = None
        with self.assertRaises(ValueError):
            Config.get()


class TestTwitterConfig(unittest.TestCase):

    def test_load_values(self):
        load_fixture_config()

        # Global settings
        self.assertEqual(TwitterConfig.get().consumer_key, "test")
        self.assertEqual(TwitterConfig.get().consumer_secret, "test")
        self.assertEqual(TwitterConfig.get().access_token_key, "test")
        self.assertEqual(TwitterConfig.get().access_token_secret, "test")
        self.assertEqual(TwitterConfig.get().min_ratelimit_percent, 10)

        # Search settings
        self.assertIsInstance(TwitterConfig.get().search.queries, list)
        self.assertEqual(len(TwitterConfig.get().search.queries), 3)
        self.assertEqual(TwitterConfig.get().search.queries[0], "test1")
        self.assertEqual(TwitterConfig.get().search.queries[1], "test2")
        self.assertIsInstance(TwitterConfig.get().search.queries[2], OrderedDict)
        self.assertIn("test3", TwitterConfig.get().search.queries[2])
        self.assertIn("lang", TwitterConfig.get().search.queries[2])
        self.assertEqual(TwitterConfig.get().search.queries[2]["test3"], None)
        self.assertEqual(TwitterConfig.get().search.queries[2]["lang"], "el")
        self.assertEqual(TwitterConfig.get().search.max_queue, 100)
        self.assertEqual(TwitterConfig.get().search.max_quote_depth, 20)
        self.assertEqual(TwitterConfig.get().search.min_quote_similarity, 0.5)
        # Filter
        self.assertEqual(TwitterConfig.get().search.filter.min_retweets.enabled, False)
        self.assertEqual(TwitterConfig.get().search.filter.min_retweets.number, 20)
        # Sort
        self.assertEqual(TwitterConfig.get().search.sort.by_keywords.enabled, True)
        self.assertEqual(TwitterConfig.get().search.sort.by_keywords.keywords, ["ps4", "pc"])

        # Actions
        self.assertEqual(TwitterConfig.get().actions.follow.enabled, True)
        self.assertEqual(TwitterConfig.get().actions.follow.multiple, False)
        self.assertEqual(TwitterConfig.get().actions.follow.keywords, ["follow", "follower"])
        self.assertEqual(TwitterConfig.get().actions.follow.max_following, 1950)
        self.assertEqual(TwitterConfig.get().actions.favorite.enabled, True)
        self.assertEqual(TwitterConfig.get().actions.favorite.keywords, ["fav", "favorite"])
        self.assertEqual(TwitterConfig.get().actions.tag_friend.enabled, True)
        self.assertEqual(TwitterConfig.get().actions.tag_friend.friends, ["friend1", "friend2", "friend3"])
        self.assertEqual(TwitterConfig.get().actions.tag_friend.friend_keywords, ["friend", "friends"])
        self.assertEqual(TwitterConfig.get().actions.tag_friend.tag_keywords, ["tag"])

        # Scheduler
        self.assertEqual(TwitterConfig.get().scheduler.search_interval, 5400)
        self.assertEqual(TwitterConfig.get().scheduler.retweet_interval, 600)
        self.assertEqual(TwitterConfig.get().scheduler.retweet_random_margin, 60)
        self.assertEqual(TwitterConfig.get().scheduler.blocked_users_update_interval, 300)
        self.assertEqual(TwitterConfig.get().scheduler.clear_queue_interval, 60)
        self.assertEqual(TwitterConfig.get().scheduler.rate_limit_update_interval, 60)
        self.assertEqual(TwitterConfig.get().scheduler.check_mentions_interval, 600)


class TestNotifiersConfig(unittest.TestCase):

    def test_load_values(self):
        load_fixture_config()

        # Pushbullet
        self.assertEqual(NotifiersConfig.get().pushbullet.enabled, False)
        self.assertEqual(NotifiersConfig.get().pushbullet.token, "test")

        # Email
        self.assertEqual(NotifiersConfig.get().mail.enabled, False)
        self.assertEqual(NotifiersConfig.get().mail.host, 'smtp.provider.com')
        self.assertEqual(NotifiersConfig.get().mail.port, 25)
        self.assertEqual(NotifiersConfig.get().mail.tls, False)
        self.assertEqual(NotifiersConfig.get().mail.username, 'sender_address@provider.com')
        self.assertEqual(NotifiersConfig.get().mail.password, 'my_secure_password')
        self.assertEqual(NotifiersConfig.get().mail.recipient, 'sender_address@provider.com')
