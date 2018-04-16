import unittest

from tests.helper_func import load_fixture_config, create_post
from yatcobot.config import TwitterConfig, Config
from yatcobot.plugins.filters import FilterABC, FilterMinRetweets, FilterBlacklist
from yatcobot.post_queue import PostQueue


class TestFilterABC(unittest.TestCase):

    def setUp(self):
        load_fixture_config()

    def test_get_enabled(self):
        for method in TwitterConfig.get().search.filter.values():
            method['enabled'] = True
        self.assertEqual(len(FilterABC.get_enabled()), len(TwitterConfig.get().search.filter))

        for method in TwitterConfig.get().search.filter.values():
            method['enabled'] = False
        self.assertEqual(len(FilterABC.get_enabled()), 0)


class TestFilterMinRetweets(unittest.TestCase):

    def setUp(self):
        load_fixture_config()
        self.method = FilterMinRetweets()

    def test_filter(self):
        TwitterConfig.get()['search']['filter']['min_retweets']['enabled'] = True
        TwitterConfig.get()['search']['filter']['min_retweets']['number'] = 10

        posts = {
            1: create_post(id=1, retweets=1),
            2: create_post(id=2, retweets=5),
            3: create_post(id=3, retweets=15),
            4: create_post(id=4, retweets=20),
        }

        queue = PostQueue(posts)

        self.method.filter(queue)

        self.assertEqual(len(queue), 2)

        for post_id, post in queue.items():
            self.assertGreaterEqual(post['retweet_count'], 10)

    def test_enabled(self):
        TwitterConfig.get()['search']['filter']['min_retweets']['enabled'] = True
        self.assertTrue(self.method.is_enabled())

        TwitterConfig.get()['search']['filter']['min_retweets']['enabled'] = False
        self.assertFalse(self.method.is_enabled())

    def test_config(self):
        template = Config.get_template()
        self.assertIn(FilterMinRetweets.name, template['twitter']['search']['filter'])
        self.assertIn('enabled', template['twitter']['search']['filter'][FilterMinRetweets.name])
        self.assertIn('number', template['twitter']['search']['filter'][FilterMinRetweets.name])


class TestFilterKeywordsBlacklist(unittest.TestCase):

    def setUp(self):
        load_fixture_config()
        self.method = FilterBlacklist()

    def test_filter_keywords(self):
        TwitterConfig.get()['search']['filter']['blacklist']['enabled'] = True
        TwitterConfig.get()['search']['filter']['blacklist']['keywords'] = ['keyword']

        posts = {
            1: create_post(id=1, full_text='should be fine'),
            2: create_post(id=2, full_text='contains keyword'),
        }

        queue = PostQueue(posts)

        self.method.filter(queue)

        self.assertEqual(len(queue), 1)

        for post_id, post in queue.items():
            self.assertNotIn('keyword', post['full_text'])

    def test_filter_keywords_empty(self):
        TwitterConfig.get()['search']['filter']['blacklist']['enabled'] = True
        TwitterConfig.get()['search']['filter']['blacklist']['keywords'] = list()

        posts = {
            1: create_post(id=1, full_text='should be fine'),
            2: create_post(id=2, full_text='contains keyword'),
        }
        queue = PostQueue(posts)

        self.method.filter(queue)

        self.assertEqual(len(queue), 2)

    def test_filter_users(self):
        TwitterConfig.get()['search']['filter']['blacklist']['enabled'] = True
        TwitterConfig.get()['search']['filter']['blacklist']['users'] = ['bad_user']

        posts = {
            1: create_post(id=1, screen_name='good_user'),
            2: create_post(id=2, screen_name='Bad_user'),
        }

        queue = PostQueue(posts)

        self.method.filter(queue)

        self.assertEqual(len(queue), 1)

        for post_id, post in queue.items():
            self.assertNotEqual('bad_user', post['user']['screen_name'])

    def test_enabled(self):
        TwitterConfig.get()['search']['filter']['blacklist']['enabled'] = True
        self.assertTrue(self.method.is_enabled())

        TwitterConfig.get()['search']['filter']['blacklist']['enabled'] = False
        self.assertFalse(self.method.is_enabled())

    def test_config(self):
        template = Config.get_template()
        self.assertIn(FilterBlacklist.name, template['twitter']['search']['filter'])
        self.assertIn('enabled', template['twitter']['search']['filter'][FilterBlacklist.name])
        self.assertIn('keywords', template['twitter']['search']['filter'][FilterBlacklist.name])
