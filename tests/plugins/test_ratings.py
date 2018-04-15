import unittest

from tests.helper_func import load_fixture_config, create_post
from yatcobot.config import TwitterConfig, Config
from yatcobot.plugins.ratings import RatingABC, RatingByRetweetsCount, RatingByKeywords, RatingByAge
from yatcobot.post_queue import PostQueue


class TestRateABC(unittest.TestCase):

    def setUp(self):
        load_fixture_config()

    def test_get_enabled(self):
        for method in TwitterConfig.get().search.sort.values():
            method['enabled'] = True
        self.assertEqual(len(RatingABC.get_enabled()), len(TwitterConfig.get().search.sort))

        for method in TwitterConfig.get().search.sort.values():
            method['enabled'] = False
        self.assertEqual(len(RatingABC.get_enabled()), 0)


class TestRateByRetweetCount(unittest.TestCase):

    def setUp(self):
        load_fixture_config()
        self.method = RatingByRetweetsCount()

    def test_get_retweets_rate(self):
        TwitterConfig.get()['search']['sort']['by_retweets_count']['enabled'] = True

        posts = dict()
        for i in range(10):
            post = create_post()
            posts[post['id']] = post

        queue = PostQueue(posts)
        rates = self.method.get_rating(queue)

        self.assertEqual(len(rates), len(posts))

        sorted_rates = sorted(((x.id, x.score) for x in rates), key=lambda x: x[1], reverse=True)

        previous = sorted_rates.pop(0)[0]
        for id, rate in sorted_rates:
            self.assertLessEqual(posts[id]['retweet_count'], posts[previous]['retweet_count'])
            previous = id

    def test_enabled(self):
        TwitterConfig.get()['search']['sort']['by_retweets_count']['enabled'] = True
        self.assertTrue(self.method.is_enabled())

        TwitterConfig.get()['search']['sort']['by_retweets_count']['enabled'] = False
        self.assertFalse(self.method.is_enabled())

    def test_config(self):
        template = Config.get_template()
        self.assertIn(RatingByRetweetsCount.name, template['twitter']['search']['sort'])
        self.assertIn('enabled', template['twitter']['search']['sort'][RatingByRetweetsCount.name])


class TestRateByKeywords(unittest.TestCase):

    def setUp(self):
        load_fixture_config()
        self.method = RatingByKeywords()

    def test_get_keywords_rate(self):
        TwitterConfig.get()['search']['sort']['by_keywords']['enabled'] = True
        TwitterConfig.get()['search']['sort']['by_keywords']['keywords'] = ["Test"]

        posts = {
            1: create_post(id=1, full_text="Test"),
            2: create_post(id=2, full_text="test"),
            3: create_post(id=3, full_text="norate"),
            4: create_post(id=4, full_text="test test"),
        }

        queue = PostQueue(posts)

        rates = self.method.get_rating(queue)

        rates = {x.id: x.score for x in rates}
        self.assertEqual(rates[1], rates[2])
        self.assertLess(rates[3], rates[2])
        self.assertGreater(rates[4], rates[2])

    def test_enabled(self):
        TwitterConfig.get()['search']['sort']['by_keywords']['enabled'] = True
        self.assertTrue(self.method.is_enabled())

        TwitterConfig.get()['search']['sort']['by_keywords']['enabled'] = False
        self.assertFalse(self.method.is_enabled())

    def test_config(self):
        template = Config.get_template()
        self.assertIn(RatingByKeywords.name, template['twitter']['search']['sort'])
        self.assertIn('enabled', template['twitter']['search']['sort'][RatingByKeywords.name])
        self.assertIn('keywords', template['twitter']['search']['sort'][RatingByKeywords.name])


class TestRateAge(unittest.TestCase):

    def setUp(self):
        load_fixture_config()
        self.method = RatingByAge()

    def test_get_age_rate(self):
        posts = {
            1: create_post(id=1, date='Thu Oct 08 08:34:51 +0000 2015'),
            2: create_post(id=2, date='Thu Oct 07 08:34:51 +0000 2015'),
            3: create_post(id=3, date='Thu Oct 06 08:34:51 +0000 2015'),
            4: create_post(id=4, date='Thu Oct 05 08:34:51 +0000 2015'),
        }

        queue = PostQueue(posts)

        rates = self.method.get_rating(queue)
        rates = {x.id: x.score for x in rates}
        self.assertGreater(rates[1], rates[2])
        self.assertGreater(rates[2], rates[3])
        self.assertGreater(rates[3], rates[4])

    def test_enabled(self):
        TwitterConfig.get()['search']['sort']['by_age']['enabled'] = True
        self.assertTrue(self.method.is_enabled())

        TwitterConfig.get()['search']['sort']['by_age']['enabled'] = False
        self.assertFalse(self.method.is_enabled())

    def test_config(self):
        template = Config.get_template()
        self.assertIn(RatingByAge.name, template['twitter']['search']['sort'])
        self.assertIn('enabled', template['twitter']['search']['sort'][RatingByAge.name])
