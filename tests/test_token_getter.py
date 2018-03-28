import builtins
import logging
import os
import unittest
from unittest.mock import MagicMock

import requests_mock

import yatcobot.token_getter
from yatcobot.token_getter import get_access_token

logging.disable(logging.ERROR)


class TestTokenGetter(unittest.TestCase):
    tests_path = os.path.dirname(os.path.abspath(__file__))

    def _set_up_mock(self, m):
        with open(self.tests_path + '/fixtures/oauth_request_token') as f:
            response = f.read()
        m.post('https://api.twitter.com/oauth/request_token', text=response)

        with open(self.tests_path + '/fixtures/oauth_access_token') as f:
            response = f.read()
        m.post('https://api.twitter.com/oauth/access_token', text=response)

    def setUp(self):
        yatcobot.token_getter.webbrowser = MagicMock()
        builtins.input = MagicMock()
        builtins.input.return_value = '123456'

    @requests_mock.mock()
    def test_get_auth(self, m):
        self._set_up_mock(m)

        tokens = get_access_token('test', 'test')
        self.assertEqual(tokens['secret'], '2EEfA6BG3ly3sR3RjE0IBSnlQu4ZrUzPiYKmrkVU')
        self.assertEqual(tokens['token'], '6253282-eWudHldSbIaelX7swmsiHImEL4KinwaGloHANdrY')
