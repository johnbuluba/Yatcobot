import logging
import unittest

from tests.helper_func import create_post, load_fixture_config
from yatcobot.post_queue import *

logging.disable(logging.ERROR)


class TestPostQueueSorter(unittest.TestCase):

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

    def test_filter_queue(self):
        Config.get_config()['search']['filter']['min_retweets']['enabled'] = True
        Config.get_config()['search']['filter']['min_retweets']['number'] = 5

        posts = dict()
        for i in range(10):
            post = create_post(retweets=i)
            posts[post['id']] = post

        queue = PostQueue(posts)

        queue.filter()
        for post in queue.values():
            self.assertGreaterEqual(post['retweet_count'], 5)



class TestRateByRetweetCount(unittest.TestCase):

    def setUp(self):
        load_fixture_config()
        self.method = RateByRetweetsCount()

    def test_get_retweets_rate(self):
        Config.get_config()['search']['sort']['by_retweets_count']['enabled'] = True

        posts = dict()
        for i in range(10):
            post = create_post()
            posts[post['id']] = post

        queue = PostQueue(posts)
        rates = self.method.get_rates(queue)

        self.assertEqual(len(rates), len(posts))
        
        sorted_rates = sorted(((x.id, x.score) for x in rates), key=lambda x: x[1], reverse=True)
        
        previous = sorted_rates.pop(0)[0]
        for id, rate in sorted_rates:
            self.assertLessEqual(posts[id]['retweet_count'], posts[previous]['retweet_count'])
            previous = id


class TestRateByKeywords(unittest.TestCase):

    def setUp(self):
        load_fixture_config()
        self.method = RateByKeywords()

    def test_get_keywords_rate(self):
        Config.get_config()['search']['sort']['by_keywords']['enabled'] = True
        Config.get_config()['search']['sort']['by_keywords']['keywords'] = ["Test"]

        posts = {
            1: create_post(id=1, full_text="Test"),
            2: create_post(id=2, full_text="test"),
            3: create_post(id=3, full_text="norate"),
            4: create_post(id=4, full_text="test test"),
        }

        queue = PostQueue(posts)

        rates = self.method.get_rates(queue)

        rates = {x.id: x.score for x in rates}
        self.assertEqual(rates[1], rates[2])
        self.assertLess(rates[3], rates[2])
        self.assertGreater(rates[4], rates[2])


class TestRateAge(unittest.TestCase):

    def setUp(self):
        load_fixture_config()
        self.method = RateByAge()

    def test_get_age_rate(self):
        posts = {
            1: create_post(id=1, date='Thu Oct 08 08:34:51 +0000 2015'),
            2: create_post(id=2, date='Thu Oct 07 08:34:51 +0000 2015'),
            3: create_post(id=3, date='Thu Oct 06 08:34:51 +0000 2015'),
            4: create_post(id=4, date='Thu Oct 05 08:34:51 +0000 2015'),
        }

        queue = PostQueue(posts)

        rates = self.method.get_rates(queue)
        rates = {x.id: x.score for x in rates}
        self.assertGreater(rates[1], rates[2])
        self.assertGreater(rates[2], rates[3])
        self.assertGreater(rates[3], rates[4])


class TestFilterMinRetweets(unittest.TestCase):

    def setUp(self):
        load_fixture_config()
        self.method = FilterMinRetweets()

    def test_filter_by_min_retweets(self):
        Config.get_config()['search']['filter']['min_retweets']['enabled'] = True
        Config.get_config()['search']['filter']['min_retweets']['number'] = 10

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


