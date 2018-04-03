import logging
import unittest

from tests.helper_func import create_post, load_fixture_config
from yatcobot.config import TwitterConfig
from yatcobot.post_queue import *

logging.disable(logging.ERROR)


class TestPostQueue(unittest.TestCase):

    def setUp(self):
        load_fixture_config()

    def test_sort_queue(self):
        posts = dict()
        for i in range(10):
            post = create_post()
            posts[post['id']] = post

        queue = PostQueue(posts)

        queue.sort()

        key, previous = queue.popitem(last=False)
        for post in queue.values():
            self.assertLessEqual(post['score'], previous['score'])

    def test_sort_queue_len_1(self):
        """If less than 2, raises StatisticsError('variance requires at least two data points')"""
        posts = dict()
        post = create_post()
        posts[post['id']] = post

        queue = PostQueue(posts)

        queue.sort()

        key, previous = queue.popitem(last=False)
        for post in queue.values():
            self.assertLessEqual(post['score'], previous['score'])

    def test_filter_queue(self):
        TwitterConfig.get()['search']['filter']['min_retweets']['enabled'] = True
        TwitterConfig.get()['search']['filter']['min_retweets']['number'] = 5

        posts = dict()
        for i in range(10):
            post = create_post(retweets=i)
            posts[post['id']] = post

        queue = PostQueue(posts)

        queue.filter()
        for post in queue.values():
            self.assertGreaterEqual(post['retweet_count'], 5)
