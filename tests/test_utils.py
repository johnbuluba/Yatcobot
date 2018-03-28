import logging
import unittest

from yatcobot.utils import create_keyword_mutations

logging.disable(logging.ERROR)


class TestUtils(unittest.TestCase):

    def test_get_keyword_mutations(self):
        keyword = 'keyword'
        target_mutations = ['#keyword', ' keyword ', '.keyword', 'keyword ', ' keyword', 'keyword.', ',keyword',
                            'keyword,']
        mutations = create_keyword_mutations(keyword)
        self.assertEqual(len(mutations), len(target_mutations))
        for mutation in mutations:
            self.assertIn(mutation, target_mutations)
