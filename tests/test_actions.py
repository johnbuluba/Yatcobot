import logging
import random
import unittest
from unittest.mock import patch

from yatcobot.actions import Favorite, Follow
from yatcobot.config import Config

logging.disable(logging.ERROR)


class TestFollow(unittest.TestCase):

    @patch('yatcobot.bot.TwitterClient')
    @patch('yatcobot.bot.Config')
    def setUp(self, config_mock, client_mock):
        self.config = config_mock
        self.client = client_mock
        self.action = Follow(self.client)

    def test_follow(self):
        Config.follow_keywords = [' follow ']

        post = (
            {'id': 0, 'full_text': 'test follow tests', 'user': {'id': random.randint(1, 1000), 'screen_name': 'test'},
             'retweeted': False})

        self.action.process(post)
        self.client.follow.assert_called_once_with(post['user']['screen_name'])

    def test_no_follow(self):
        Config.follow_keywords = [' follow ']

        post = (
            {'id': 0, 'full_text': 'test tests', 'user': {'id': random.randint(1, 1000), 'screen_name': 'test'},
             'retweeted': False})

        self.action.process(post)
        self.assertFalse(self.client.follow.called)

    def test_follow_with_remove_oldest(self):
        Config.follow_keywords = [' follow ']

        post = (
            {'id': 0, 'full_text': 'test follow tests', 'user': {'id': random.randint(1, 1000), 'screen_name': 'test'},
             'retweeted': False})

        follows = [x for x in range(Config.max_follows + 1)]
        self.client.get_friends_ids.return_value = follows

        self.action.process(post)
        self.client.follow.assert_called_once_with(post['user']['screen_name'])
        self.client.unfollow.assert_called_with(Config.max_follows)

    def test_remove_oldest_follow_empty(self):
        follows = [x for x in range(Config.max_follows - 1)]
        self.client.get_friends_ids.return_value = follows
        self.action.remove_oldest_follow()
        self.assertFalse(self.client.unfollow.called)

    def test_remove_oldest_follow_full(self):
        follows = [x for x in range(Config.max_follows + 1)]
        self.client.get_friends_ids.return_value = follows
        self.action.remove_oldest_follow()
        self.client.unfollow.assert_called_with(Config.max_follows)


class TestFavorite(unittest.TestCase):

    @patch('yatcobot.bot.TwitterClient')
    @patch('yatcobot.bot.Config')
    def setUp(self, config_mock, client_mock):
        self.config = config_mock
        self.client = client_mock
        self.action = Favorite(self.client)

    def test_favorite(self):
        self.action = Favorite(self.client)

        Config.fav_keywords = [' favorite ']
        post = (
            {'id': 0, 'full_text': 'test favorite tests',
             'user': {'id': random.randint(1, 1000), 'screen_name': 'test'},
             'retweeted': False})

        self.action.process(post)

        self.client.favorite.assert_called_once_with(post['id'])
