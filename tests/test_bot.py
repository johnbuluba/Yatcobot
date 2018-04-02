import json
import logging
import os
import random
import unittest
from collections import OrderedDict
from unittest.mock import patch, MagicMock

from tests.helper_func import create_post, load_fixture_config
from yatcobot.bot import Yatcobot, TwitterConfig, PeriodicScheduler
from yatcobot.client import TwitterClientRetweetedException

NotficationService = patch('yatcobot.bot.NotificationService').start()

logging.disable(logging.ERROR)


class TestBot(unittest.TestCase):
    tests_path = path = os.path.dirname(os.path.abspath(__file__))

    @patch('yatcobot.bot.TwitterClient')
    @patch('yatcobot.bot.IgnoreList')
    @patch('yatcobot.bot.TwitterConfig')
    def setUp(self, config_mock, ignore_list_mock, client_mock):
        load_fixture_config()
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

    def test_get_quoted_tweet_similar(self):
        quoted = {'id': 1, 'full_text': 'test'}
        post = {'id': 2, 'full_text': 'test', 'quoted_status': quoted}
        quoted_post_full = {'id': 1, 'full_text': 'test', 'user': {'id:1'}}
        self.bot.client.get_tweet.return_value = quoted_post_full

        r = self.bot._get_quoted_tweet(post)
        self.assertEqual(r, quoted_post_full)

    def test_get_quoted_tweet_quote_of_quotes(self):

        def mock_return(id):
            return mock_return.posts[id]

        mock_return.posts = dict()
        mock_return.posts[1] = {'id': 1, 'full_text': 'test', 'user': {'id:1'}}
        mock_return.posts[2] = {'id': 2, 'full_text': 'test', 'quoted_status': mock_return.posts[1]}
        mock_return.posts[3] = {'id': 3, 'full_text': 'test', 'quoted_status': mock_return.posts[2]}

        self.bot.client.get_tweet.side_effect = mock_return

        r = self.bot._get_quoted_tweet(mock_return.posts[3])
        self.assertEqual(r, mock_return.posts[1])

    def test_get_quoted_tweet_not_similar(self):
        quoted = {'id': 1, 'full_text': 'test'}
        post = {'id': 2, 'full_text': 'test sdfsdfsf', 'quoted_status': quoted}
        quoted_post_full = {'id': 1, 'full_text': 'test', 'user': {'id:1'}}
        self.bot.client.get_tweet.return_value = quoted_post_full

        r = self.bot._get_quoted_tweet(post)
        self.assertEqual(r, post)

    def test_get_quoted_tweet_real_post(self):
        with open(self.tests_path + '/fixtures/post_with_quote.json') as f:
            post = json.load(f)
        quoted_post_full = post.copy()
        quoted_post_full['user'] = {'id': 1}
        self.bot.client.get_tweet.return_value = quoted_post_full

        r = self.bot._get_quoted_tweet(post)
        self.assertEqual(r, quoted_post_full)

    def test_clear_queue_empty(self):
        TwitterConfig.get()['search']['max_queue'] = 60
        self.bot.post_queue = MagicMock()
        self.bot.post_queue.__len__.return_value = 0
        self.bot.clear_queue()
        self.assertFalse(self.bot.post_queue.popitem.called)

    def test_clear_queue_full(self):
        TwitterConfig.get()['search']['max_queue'] = 60
        self.bot.post_queue = MagicMock()
        self.bot.post_queue.__len__.return_value = TwitterConfig.get()['search']['max_queue'] + 1

        self.bot.clear_queue()
        self.assertTrue(self.bot.post_queue.popitem.called)
        self.bot.post_queue.popitem.assert_called_with()

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
        self.assertEqual(mock_scheduler.enter.call_count, 5)
        self.assertEqual(mock_scheduler.enter_random.call_count, 1)
        self.assertTrue(mock_scheduler.run.called)

    def test_enter_contest_simple_post(self):
        posts = 10
        for i in range(posts):
            self.bot.post_queue[i] = {'id': i, 'full_text': 'test', 'score': 0,
                                      'user': {'id': random.randint(1, 1000), 'screen_name': 'test'},
                                      'retweeted': False
                                      }
        queue_copy = self.bot.post_queue.copy()
        self.bot.client.get_tweet = lambda x: queue_copy[x]

        self.bot.enter_contest()

        self.assertEqual(len(self.bot.post_queue), posts - 1)
        self.assertTrue(self.bot.client.retweet.called)
        self.bot.client.retweet.assert_called_with(0)

    def test_enter_contest_already_retweeted_found_from_failed_retweet(self):
        posts = 10
        self.bot.ignore_list = list()
        for i in range(posts):
            self.bot.post_queue[i] = {'id': i,
                                      'full_text': 'test', 'score': 0,
                                      'user': {'id': random.randint(1, 1000)},
                                      'retweeted': False
                                      }
        queue_copy = self.bot.post_queue.copy()
        self.bot.client.retweet.side_effect = TwitterClientRetweetedException()
        self.bot.client.get_tweet = lambda x: queue_copy[x]

        self.bot.enter_contest()

        self.assertEqual(len(self.bot.post_queue), posts - 1)
        self.assertTrue(self.bot.client.retweet.called)
        self.bot.client.retweet.assert_called_with(0)

        self.assertIn(0, self.bot.ignore_list)

    def test_enter_contest_already_retweeted_found_from_getting_post(self):
        posts = 10
        self.bot.ignore_list = list()
        for i in range(posts):
            self.bot.post_queue[i] = {'id': i,
                                      'full_text': 'test', 'score': 0,
                                      'user': {'id': random.randint(1, 1000)},
                                      'retweeted': True
                                      }
        queue_copy = self.bot.post_queue.copy()
        self.bot.client.get_tweet = lambda x: queue_copy[x]

        self.bot.enter_contest()

        self.assertEqual(len(self.bot.post_queue), posts - 1)
        self.assertFalse(self.bot.client.retweet.called)

        self.assertIn(0, self.bot.ignore_list)

    def test_enter_contest_skip_already_retweeted(self):
        TwitterConfig.get()['search']['skip_retweeted'] = True
        posts = 10
        self.bot.ignore_list = list()
        for i in range(posts):
            self.bot.post_queue[i] = {'id': i,
                                      'full_text': 'test', 'score': 0,
                                      'user': {'id': random.randint(1, 1000)},
                                      'retweeted': True
                                      }
        self.bot.post_queue[9]['retweeted'] = False
        queue_copy = self.bot.post_queue.copy()
        self.bot.client.get_tweet = lambda x: queue_copy[x]

        self.bot.enter_contest()

        self.assertEqual(len(self.bot.post_queue), 0)
        self.assertTrue(self.bot.client.retweet.called)
        self.bot.client.retweet.assert_called_with(9)

        self.assertListEqual([x for x in range(10)], self.bot.ignore_list)

    def test_enter_contest_skip_already_retweeted_all_retweeted(self):
        TwitterConfig.get()['search']['skip_retweeted'] = True
        posts = 10
        self.bot.ignore_list = list()
        for i in range(posts):
            self.bot.post_queue[i] = {'id': i,
                                      'full_text': 'test', 'score': 0,
                                      'user': {'id': random.randint(1, 1000)},
                                      'retweeted': True
                                      }
        queue_copy = self.bot.post_queue.copy()
        self.bot.client.get_tweet = lambda x: queue_copy[x]

        self.bot.enter_contest()

        self.assertEqual(len(self.bot.post_queue), 0)
        self.assertFalse(self.bot.client.retweet.called)

        self.assertListEqual([x for x in range(10)], self.bot.ignore_list)

    def test_enter_contest_ignored_id(self):
        posts = 10
        self.bot.ignore_list = [0]
        for i in range(posts):
            self.bot.post_queue[i] = {'id': i, 'full_text': 'test', 'score': 0, 'user': {'id': 0}}

        self.bot.enter_contest()

        self.assertEqual(len(self.bot.post_queue), posts - 1)
        self.assertFalse(self.bot.client.retweet.called)

    def test_insert_post_to_queue(self):
        post = {'id': 0, 'full_text': 'test', 'user': {'id': random.randint(1, 1000), 'screen_name': 'test'},
                'retweeted': False}

        self.bot._insert_post_to_queue(post)

        self.assertIn(post['id'], self.bot.post_queue)

    def test_insert_post_to_queue_ignore(self):
        post = {'id': 0, 'full_text': 'test', 'user': {'id': random.randint(1, 1000), 'screen_name': 'test'},
                'retweeted': False}
        self.bot.ignore_list = [0]
        self.bot._insert_post_to_queue(post)

        self.assertNotIn(post['id'], self.bot.post_queue)

    def test_insert_post_to_queue_retweeted(self):
        post = {'id': 0, 'full_text': 'test', 'user': {'id': random.randint(1, 1000), 'screen_name': 'test'},
                'retweeted': True}
        self.bot.ignore_list = [0]
        self.bot._insert_post_to_queue(post)

        self.assertNotIn(post['id'], self.bot.post_queue)

    def test_insert_post_to_queue_blocked_user(self):
        post = {'id': 0, 'text': 'test', 'user': {'id': 1, 'screen_name': 'test'}, 'retweeted': False}
        self.bot.ignore_list = [1]
        self.bot._insert_post_to_queue(post)

        self.assertNotIn(post['id'], self.bot.post_queue)

    def test_insert_post_to_queue_that_has_a_quote_thats_deleted(self):
        with open(self.tests_path + '/fixtures/deleted_quote.json') as f:
            post = json.load(f)

        self.bot._insert_post_to_queue(post)

        self.assertNotIn(post['id'], self.bot.post_queue)

    def test_scan_new_contests(self):
        TwitterConfig.get()['search']['queries'] = ['test1']
        posts = list()
        for i in range(2):
            posts.append({'id': i, 'full_text': 'test', 'retweet_count': 1,
                          'user': {'id': random.randint(1, 1000), 'screen_name': 'test'}, 'retweeted': False,
                          'created_at': 'Thu Oct 08 08:34:51 +0000 2015'})

        self.bot.client = MagicMock()
        self.bot.client.search_tweets.return_value = posts

        self.bot.scan_new_contests()

        self.bot.client.search_tweets.assert_called_once_with('test1', 50)
        self.assertEqual(len(self.bot.post_queue), 2)

    def test_scan_new_contests_with_language(self):
        TwitterConfig.get()['search']['queries'] = [OrderedDict()]
        TwitterConfig.get()['search']['queries'][0]['test1'] = None
        TwitterConfig.get()['search']['queries'][0]['lang'] = 'el'

        posts = list()
        for i in range(2):
            posts.append({'id': i, 'full_text': 'test', 'retweet_count': 1,
                          'user': {'id': random.randint(1, 1000), 'screen_name': 'test'}, 'retweeted': False,
                          'created_at': 'Thu Oct 08 08:34:51 +0000 2015'})

        self.bot.client = MagicMock()
        self.bot.client.search_tweets.return_value = posts

        self.bot.scan_new_contests()

        self.bot.client.search_tweets.assert_called_once_with('test1', 50, language='el')
        self.assertEqual(len(self.bot.post_queue), 2)

    def test_check_new_mentions_empty(self):
        posts = [create_post()]
        self.bot.client.get_mentions_timeline = MagicMock(return_value=posts)

        self.bot.check_new_mentions()

        self.bot.client.get_mentions_timeline.assert_called_once_with(count=1)
        self.assertEqual(self.bot.last_mention, posts[0])

    def test_check_new_mentions(self):
        posts = [create_post()]
        self.bot.client.get_mentions_timeline = MagicMock(return_value=posts)
        self.bot.last_mention = create_post()
        last_id = self.bot.last_mention['id']

        self.bot.check_new_mentions()

        self.bot.client.get_mentions_timeline.assert_called_once_with(since_id=last_id)
        self.assertEqual(self.bot.last_mention, posts[0])
        self.assertTrue(NotficationService.return_value.send_notification.called)

    def test_check_new_mentions_no_notifiers_enabled(self):

        self.bot.client.get_mentions_timeline = MagicMock()
        self.bot.notification = MagicMock()
        self.bot.notification.is_enabled.return_value = False
        NotficationService.reset_mock()

        self.bot.check_new_mentions()

        self.assertFalse(self.bot.client.get_mentions_timeline.called)
        self.assertFalse(NotficationService.return_value.send_notification.called)
        self.assertTrue(self.bot.notification.is_enabled)
