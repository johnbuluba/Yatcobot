import unittest
import logging
import random
from unittest.mock import patch, MagicMock

import yatcobot.bot
from yatcobot.bot import Yatcobot, Config, PeriodicScheduler
from yatcobot.client import TwitterClientRetweetedException


logging.disable(logging.ERROR)


class TestBot(unittest.TestCase):

    @patch('yatcobot.bot.TwitterClient')
    @patch('yatcobot.bot.IgnoreList')
    @patch('yatcobot.bot.Config')
    def setUp(self, config_mock, ignore_list_mock, client_mock):
        self.config = config_mock
        self.client = client_mock
        self.bot = Yatcobot('test')

    def test_get_original_tweet_no_retweet(self):
        post = {'id': 1000}
        original = self.bot._get_original_tweet(post)
        self.assertEqual(post, original)

    def test_get_original_tweet_retweet(self):
        post = {'id': 1000, 'retweeted_status': {'id': 1001}}
        original = self.bot._get_original_tweet(post)
        self.assertEqual(post['retweeted_status'], original)

    def test_clear_queue_empty(self):
        Config.max_queue = 60
        self.bot.post_queue = MagicMock()
        self.bot.post_queue.__len__.return_value = 0
        self.bot.clear_queue()
        self.assertFalse(self.bot.post_queue.popitem.called)

    def test_clear_queue_full(self):
        self.config.max_queue = 60
        self.bot.post_queue = MagicMock()
        self.bot.post_queue.__len__.return_value = self.config.max_queue + 1

        self.bot.clear_queue()
        self.assertTrue(self.bot.post_queue.popitem.called)
        self.bot.post_queue.popitem.assert_called_with(last=False)

    def test_remove_oldest_follow_empty(self):
        follows = [x for x in range(Config.max_follows - 1)]
        self.bot.client.get_friends_ids.return_value = follows
        self.bot.remove_oldest_follow()
        self.assertFalse(self.bot.client.unfollow.called)

    def test_remove_oldest_follow_full(self):
        follows = [x for x in range(Config.max_follows + 1)]
        self.bot.client.get_friends_ids.return_value = follows
        self.bot.remove_oldest_follow()
        self.bot.client.unfollow.assert_called_with(Config.max_follows)

    def test_update_blocked_users(self):
        users = [x for x in range(10)]
        self.bot.ignore_list = list()
        self.bot.client.get_blocks.return_value = users
        self.bot.update_blocked_users()
        self.assertEqual(users, self.bot.ignore_list)

    def test_run(self):
        mock_scheduler = MagicMock(PeriodicScheduler)
        self.bot.scheduler = mock_scheduler
        self.bot.run()
        self.assertEqual(mock_scheduler.enter.call_count, 4)
        self.assertEqual(mock_scheduler.enter_random.call_count, 1)
        self.assertTrue(mock_scheduler.run.called)

    def test_enter_contest_simple_post(self):
        posts = 10
        for i in range(posts):
            self.bot.post_queue[i] = {'id': i, 'text': 'test', 'user': {'id': random.randint(1, 1000), 'screen_name': 'test'}}

        self.bot.enter_contest()

        self.assertEqual(len(self.bot.post_queue), posts - 1)
        self.assertTrue(self.bot.client.retweet.called)
        self.bot.client.retweet.assert_called_with(0)

    def test_enter_contest_alredy_retweeted(self):
        posts = 10
        self.bot.ignore_list = list()
        for i in range(posts):
            self.bot.post_queue[i] = {'id': i, 'text': 'test', 'user': {'id': random.randint(1, 1000)}}
        self.bot.client.retweet.side_effect = TwitterClientRetweetedException()

        self.bot.enter_contest()

        self.assertEqual(len(self.bot.post_queue), posts - 1)
        self.assertTrue(self.bot.client.retweet.called)
        self.bot.client.retweet.assert_called_with(0)

        self.assertIn(0, self.bot.ignore_list)

    def test_enter_contest_ignored_id(self):
        posts = 10
        self.bot.ignore_list = [0]
        for i in range(posts):
            self.bot.post_queue[i] = {'id': i, 'text': 'test', 'user': {'id': 0}}

        self.bot.enter_contest()

        self.assertEqual(len(self.bot.post_queue), posts - 1)
        self.assertFalse(self.bot.client.retweet.called)

    def test_insert_post_to_queue(self):
        post = {'id': 0, 'text': 'test', 'user': {'id': random.randint(1, 1000), 'screen_name': 'test'}, 'retweeted': False}

        self.bot._insert_post_to_queue(post)

        self.assertIn(post['id'], self.bot.post_queue)

    def test_insert_post_to_queue_ignore(self):
        post = {'id': 0, 'text': 'test', 'user': {'id': random.randint(1, 1000), 'screen_name': 'test'}, 'retweeted': False}
        self.bot.ignore_list = [0]
        self.bot._insert_post_to_queue(post)

        self.assertNotIn(post['id'], self.bot.post_queue)

    def test_insert_post_to_queue_retweeted(self):
        post = {'id': 0, 'text': 'test', 'user': {'id': random.randint(1, 1000), 'screen_name': 'test'}, 'retweeted': True}
        self.bot.ignore_list = [0]
        self.bot._insert_post_to_queue(post)

        self.assertNotIn(post['id'], self.bot.post_queue)

    def test_scan_new_contests(self):
        Config.search_queries = ['test1']
        posts = list()
        for i in range(2):
            posts.append({'id': i, 'text': 'test', 'user': {'id': random.randint(1, 1000), 'screen_name': 'test'}, 'retweeted': False})

        self.bot.client = MagicMock()
        self.bot.client.search_tweets.return_value = posts

        self.bot.scan_new_contests()

        self.bot.client.search_tweets.assert_called_once_with('test1', 50)
        self.assertEqual(len(self.bot.post_queue), 2)

    def test_favorite(self):
        Config.fav_keywords = [' favorite ']
        self.bot.client = MagicMock()
        post = ({'id': 0, 'text': 'test favorite tests', 'user': {'id': random.randint(1, 1000), 'screen_name': 'test'}, 'retweeted': False})

        self.bot.check_for_favorite(post)

        self.bot.client.favorite.assert_called_once_with(post['id'])

    def test_follow(self):
        Config.fav_keywords = [' follow ']
        self.bot.client = MagicMock()
        post = ({'id': 0, 'text': 'test follow tests', 'user': {'id': random.randint(1, 1000), 'screen_name': 'test'}, 'retweeted': False})

        self.bot.check_follow_request(post)

        self.bot.client.follow.assert_called_once_with(post['user']['screen_name'])

    def test_get_keyword_mutations(self):
        keyword = 'keyword'
        target_mutations = ['#keyword', ' keyword ', '.keyword', 'keyword.', ',keyword', 'keyword,']
        mutations = self.bot._get_keyword_mutations(keyword)
        self.assertEqual(len(mutations), len(target_mutations))
        for mutation in mutations:
            self.assertIn(mutation, target_mutations)