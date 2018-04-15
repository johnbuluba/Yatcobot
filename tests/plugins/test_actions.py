import logging
import random
import unittest
from unittest.mock import patch

from tests.helper_func import load_fixture_config, get_fixture
from yatcobot.config import TwitterConfig, Config
from yatcobot.plugins.actions import Favorite, Follow, TagFriend, ActionABC

logging.disable(logging.ERROR)


class TestActionABC(unittest.TestCase):

    @patch('yatcobot.bot.TwitterClient')
    @patch('yatcobot.bot.TwitterConfig')
    def setUp(self, config_mock, client_mock):
        self.config = config_mock
        self.client = client_mock
        load_fixture_config()
        self.action = Follow(self.client)

    def test_get_enabled(self):
        for action in TwitterConfig.get().actions.values():
            action['enabled'] = True
        self.assertEqual(len(ActionABC.get_enabled(self.client)), len(TwitterConfig.get().actions))

        for action in TwitterConfig.get().actions.values():
            action['enabled'] = False
        self.assertEqual(len(ActionABC.get_enabled(self.client)), 0)


class TestFollow(unittest.TestCase):

    @patch('yatcobot.bot.TwitterClient')
    @patch('yatcobot.bot.TwitterConfig')
    def setUp(self, config_mock, client_mock):
        self.config = config_mock
        self.client = client_mock
        load_fixture_config()
        self.action = Follow(self.client)

    def test_follow(self):
        TwitterConfig.get()['actions']['follow']['keywords'] = [' follow ']

        post = (
            {'id': 0, 'full_text': 'test follow tests', 'user': {'id': random.randint(1, 1000), 'screen_name': 'test'},
             'retweeted': False})

        self.action.process(post)
        self.client.follow.assert_called_once_with(post['user']['screen_name'])

    def test_no_follow(self):
        TwitterConfig.get()['actions']['follow']['keywords'] = [' follow ']

        post = (
            {'id': 0, 'full_text': 'test tests', 'user': {'id': random.randint(1, 1000), 'screen_name': 'test'},
             'retweeted': False})

        self.action.process(post)
        self.assertFalse(self.client.follow.called)

    def test_follow_with_remove_oldest(self):
        TwitterConfig.get()['actions']['follow']['keywords'] = [' follow ']

        post = (
            {'id': 0, 'full_text': 'test follow tests', 'user': {'id': random.randint(1, 1000), 'screen_name': 'test'},
             'retweeted': False})

        follows = [x for x in range(TwitterConfig.get()['actions']['follow']['max_following'] + 1)]
        self.client.get_friends_ids.return_value = follows

        self.action.process(post)
        self.client.follow.assert_called_once_with(post['user']['screen_name'])
        self.client.unfollow.assert_called_with(TwitterConfig.get()['actions']['follow']['max_following'])

    def test_remove_oldest_follow_empty(self):
        follows = [x for x in range(TwitterConfig.get()['actions']['follow']['max_following'] - 1)]
        self.client.get_friends_ids.return_value = follows
        self.action.remove_oldest_follow()
        self.assertFalse(self.client.unfollow.called)

    def test_remove_oldest_follow_full(self):
        follows = [x for x in range(TwitterConfig.get()['actions']['follow']['max_following'] + 1)]
        self.client.get_friends_ids.return_value = follows
        self.action.remove_oldest_follow()
        self.client.unfollow.assert_called_with(TwitterConfig.get()['actions']['follow']['max_following'])

    def test_multiple_follows(self):
        TwitterConfig.get()['actions']['follow']['multiple'] = True

        post = get_fixture('post_multiple_mentions.json')

        self.action.process(post)

        self.assertEqual(self.client.follow.call_count, 2)
        for user in post['entities']['user_mentions']:
            self.client.follow.assert_any_call(user['screen_name'])

    def test_enabled(self):
        TwitterConfig.get()['actions']['follow']['enabled'] = True
        self.assertTrue(self.action.is_enabled())

        TwitterConfig.get()['actions']['follow']['enabled'] = False
        self.assertFalse(self.action.is_enabled())

    def test_config(self):
        template = Config.get_template()
        self.assertIn(Follow.name, template['twitter']['actions'])
        self.assertIn('enabled', template['twitter']['actions'][Follow.name])
        self.assertIn('keywords', template['twitter']['actions'][Follow.name])
        self.assertIn('max_following', template['twitter']['actions'][Follow.name])
        self.assertIn('multiple', template['twitter']['actions'][Follow.name])


class TestFavorite(unittest.TestCase):

    @patch('yatcobot.bot.TwitterClient')
    @patch('yatcobot.bot.TwitterConfig')
    def setUp(self, config_mock, client_mock):
        self.config = config_mock
        self.client = client_mock
        self.action = Favorite(self.client)
        load_fixture_config()

    def test_favorite(self):
        self.action = Favorite(self.client)
        TwitterConfig.get()['actions']['favorite']['keywords'] = [' favorite ']

        post = (
            {'id': 0, 'full_text': 'test favorite tests',
             'user': {'id': random.randint(1, 1000), 'screen_name': 'test'},
             'retweeted': False})

        self.action.process(post)

        self.client.favorite.assert_called_once_with(post['id'])

    def test_enabled(self):
        TwitterConfig.get()['actions']['favorite']['enabled'] = True
        self.assertTrue(self.action.is_enabled())

        TwitterConfig.get()['actions']['favorite']['enabled'] = False
        self.assertFalse(self.action.is_enabled())

    def test_config(self):
        template = Config.get_template()
        self.assertIn(Favorite.name, template['twitter']['actions'])
        self.assertIn('enabled', template['twitter']['actions'][Favorite.name])
        self.assertIn('keywords', template['twitter']['actions'][Favorite.name])


class TestTagFriend(unittest.TestCase):

    @patch('yatcobot.bot.TwitterClient')
    @patch('yatcobot.bot.TwitterConfig')
    def setUp(self, config_mock, client_mock):
        load_fixture_config()
        self.config = config_mock
        self.client = client_mock
        self.action = TagFriend(self.client)

    def test_tag_needed(self):
        post = get_fixture('post_tag_one_friend.json')
        self.assertTrue(self.action.tag_needed(post))

        post['full_text'] = " Testestset asdasda testesadst astagaring!"
        self.assertFalse(self.action.tag_needed(post))

        post['full_text'] = " Testestset tag testesadst astagaring!"
        self.assertFalse(self.action.tag_needed(post))

    def test_friends_required(self):
        post = {'full_text': 'friend test test! #test tag or not a friend and tag a friend'}
        self.assertEqual(self.action.get_friends_required(post), 1)

        post = {'full_text': 'sfdsfsdhkjtag sdfskhsf friend tag ONE friend asdfsd sfsfd'}
        self.assertEqual(self.action.get_friends_required(post), 1)

        post = {'full_text': 'sfdsfsdhkjtag sdfskhsf friend tag 1 FRIEND asdfsd sfsfd'}
        self.assertEqual(self.action.get_friends_required(post), 1)

        post = {'full_text': 'hsdfsfsffrient sntagf friend and TAG two friends sfsdf'}
        self.assertEqual(self.action.get_friends_required(post), 2)

        post = {'full_text': 'hsdfsfsffrient sntagf friend and TAG 3 friends sfsdf'}
        self.assertEqual(self.action.get_friends_required(post), 3)

        post = {'full_text': 'hsdfsfsffrient sntagf friend and TAG THREE friends sfsdf'}
        self.assertEqual(self.action.get_friends_required(post), 3)

        with self.assertRaises(ValueError):
            post = {'full_text': 'sdfsdfsj tag sdfjshd friend'}
            self.action.get_friends_required(post)

        with self.assertRaises(ValueError):
            post = {'full_text': 'sdfsdfsj tag three two friend'}
            self.action.get_friends_required(post)

    def test_process(self):
        post = get_fixture('post_tag_one_friend.json')
        self.action.process(post)
        self.assertEqual(self.client.update.call_count, 1)

        post = get_fixture('post_tag_friend.json')
        self.action.process(post)
        self.assertEqual(self.client.update.call_count, 2)

    def test_process_with_error_cannot_find_substring(self):
        post = {'full_text': 'sdfsdfsj tag three two friend', 'id': 'test'}
        self.action.process(post)
        self.assertFalse(self.client.update.called)

    def test_process_with_error_cannot_find_number(self):
        post = {'full_text': 'sdfsdfsj tag three two friend', 'id': 'test'}
        self.action.process(post)
        self.assertFalse(self.client.update.called)

    def test_process_with_error_not_enough_friends(self):
        post = {'full_text': 'sdfsdfsj tag four friend', 'id': 'test'}
        self.action.process(post)
        self.assertFalse(self.client.update.called)

    def test_enabled(self):
        TwitterConfig.get()['actions']['tag_friend']['enabled'] = True
        self.assertTrue(self.action.is_enabled())

        TwitterConfig.get()['actions']['tag_friend']['enabled'] = False
        self.assertFalse(self.action.is_enabled())

    def test_config(self):
        template = Config.get_template()
        self.assertIn(TagFriend.name, template['twitter']['actions'])
        self.assertIn('enabled', template['twitter']['actions'][TagFriend.name])
        self.assertIn('friends', template['twitter']['actions'][TagFriend.name])
        self.assertIn('tag_keywords', template['twitter']['actions'][TagFriend.name])
        self.assertIn('friend_keywords', template['twitter']['actions'][TagFriend.name])
        self.assertIn('number_keywords', template['twitter']['actions'][TagFriend.name])
