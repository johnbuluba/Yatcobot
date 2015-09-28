import os
import unittest
import logging

import requests_mock

from yatcobot.main import TwitterClient


class TestTwitterClient(unittest.TestCase):
    """Tests for TwitterClient class"""

    def setUp(self):
        logging.disable(logging.ERROR)
        self.tests_path = path = os.path.dirname(os.path.abspath(__file__))
        self.client = TwitterClient('Consumer Key', "Consumer Secret", "Access Key", "Access Secret")

    @requests_mock.mock()
    def test_search_tweets(self, m):
        with open(self.tests_path + '/fixtures/search_tweets.json') as f:
            response = f.read()
        m.get('https://api.twitter.com/1.1/search/tweets.json?q=210462857140252672&result_type=mixed&count=50',
                                                                                                    text=response)
        r = self.client.search_tweets("210462857140252672", 50)
        self.assertEqual(len(r), 4)

    @requests_mock.mock()
    def test_retweet(self, m):
        with open(self.tests_path + '/fixtures/statuses_retweet.json') as f:
            response = f.read()
        m.post('https://api.twitter.com/1.1/statuses/retweet/241259202004267009.json', text=response)
        r = self.client.retweet("241259202004267009")
        self.assertEqual(r['retweeted_status']['id'], 241259202004267009)

    @requests_mock.mock()
    def test_get_tweet(self, m):
        with open(self.tests_path + '/fixtures/statuses_show.json') as f:
            response = f.read()
        m.get('https://api.twitter.com/1.1/statuses/show/210462857140252672.json', text=response)
        r = self.client.get_tweet("210462857140252672")
        self.assertEqual(r['id'], 210462857140252672)

    @requests_mock.mock()
    def test_get_friends_ids(self, m):
        with open(self.tests_path + '/fixtures/friends_ids.json') as f:
            response = f.read()
        m.get('https://api.twitter.com/1.1/friends/ids.json', text=response)
        r = self.client.get_friends_ids()
        self.assertEqual(len(r), 31)

    @requests_mock.mock()
    def test_follow(self, m):
        with open(self.tests_path + '/fixtures/friendship_create.json') as f:
            response = f.read()
        m.post('https://api.twitter.com/1.1/friendships/create.json', text=response)
        r = self.client.follow(1401881)
        self.assertEqual(r['id'], 1401881)








