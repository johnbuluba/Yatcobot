import unittest

import confuse

from yatcobot.config.templates import NumberKeywordsTemplate


class TestNumberKeywordsTemplates(unittest.TestCase):

    def test_number_keywords_template(self):
        data = confuse.ConfigSource.of({1: ["test"], 2: 'test'})
        view = confuse.RootView([data])
        view.set(data)
        r = view.get(NumberKeywordsTemplate())

        self.assertDictEqual(r, {1: ["test"], 2: ["test"]})

        self.assertEqual(str(NumberKeywordsTemplate()), 'NumberKeywordsTemplate()')

        view.set(confuse.ConfigSource.of({'not_int': ["test"], 2: 'test'}))
        with self.assertRaises(confuse.ConfigTypeError):
            r = view.get(NumberKeywordsTemplate())
