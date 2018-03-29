import logging
import unittest

from tests.helper_func import create_post, load_fixture_config
from yatcobot.post_queue import *

logging.disable(logging.ERROR)


class TestPostQueueSorter(unittest.TestCase):

    def setUp(self):
        load_fixture_config()

    def test_get_retweets_score(self):
        posts = dict()
        for i in range(10):
            post = create_post()
            posts[post['id']] = post

        queue = PostQueue(posts)
        scores = queue.get_retweets_score()

        self.assertEqual(len(scores), len(posts))
        sorted_scores = sorted(((x.id, x.score) for x in scores), key=lambda x: x[1], reverse=True)
        previous = sorted_scores.pop(0)[0]
        for id, score in sorted_scores:
            self.assertLessEqual(posts[id]['retweet_count'], posts[previous]['retweet_count'])
            previous = id

    def test_get_keywords_score(self):
        Config.get_config()['search']['priority_keywords'] = ["Test"]
        posts = {
            1: create_post(id=1, full_text="Test"),
            2: create_post(id=2, full_text="test"),
            3: create_post(id=3, full_text="noscore"),
            4: create_post(id=4, full_text="test test"),
        }

        queue = PostQueue(posts)

        scores = queue.get_keywords_score()
        scores = {x.id: x.score for x in scores}
        self.assertEqual(scores[1], scores[2])
        self.assertLess(scores[3], scores[2])
        self.assertGreater(scores[4], scores[2])

    def test_get_age_score(self):
        posts = {
            1: create_post(id=1, date='Thu Oct 08 08:34:51 +0000 2015'),
            2: create_post(id=2, date='Thu Oct 07 08:34:51 +0000 2015'),
            3: create_post(id=3, date='Thu Oct 06 08:34:51 +0000 2015'),
            4: create_post(id=4, date='Thu Oct 05 08:34:51 +0000 2015'),
        }

        queue = PostQueue(posts)

        scores = queue.get_age_score()
        scores = {x.id: x.score for x in scores}
        self.assertGreater(scores[1], scores[2])
        self.assertGreater(scores[2], scores[3])
        self.assertGreater(scores[3], scores[4])

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
