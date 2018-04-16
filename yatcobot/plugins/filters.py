import logging
from abc import abstractmethod

import confuse

from yatcobot.config import TwitterConfig
from yatcobot.plugins import PluginABC, MergeAllSubclassesConfigsMixin, GetEnabledSubclassesMixin
from yatcobot.utils import create_keyword_mutations, count_keyword_in_text, preprocess_text

logger = logging.getLogger(__name__)


class FilterABC(MergeAllSubclassesConfigsMixin, GetEnabledSubclassesMixin, PluginABC):
    """
    Superclass of filtering methods for filtering the queue
    """

    @abstractmethod
    def filter(self, queue):
        """Subclasses must implement filter"""


class FilterMinRetweets(FilterABC):
    name = 'min_retweets'

    def filter(self, queue):
        """
        Removes all post that have less rewteets than min_retweets defined at config
        :param queue: Posts Queue
        """
        ids_to_remove = list()

        for post_id, post in queue.items():
            if post['retweet_count'] < TwitterConfig.get().search.filter.min_retweets.number:
                logger.info('Skipping {} because it has {} retweets'.format(post_id, post['retweet_count']))
                ids_to_remove.append(post_id)

        for post_id in ids_to_remove:
            del queue[post_id]

    @staticmethod
    def is_enabled():
        return TwitterConfig.get().search.filter.min_retweets.enabled

    @staticmethod
    def get_config_template():
        template = {
            'enabled': confuse.TypeTemplate(bool),
            'number': confuse.Integer()
        }
        return template


class FilterBlacklist(FilterABC):
    name = 'blacklist'

    def filter(self, queue):
        """
        Removes all post that contains some keywords in text
        :param queue: Posts Queue
        """

        ids_to_remove = list()

        for post_id, post in queue.items():
            # Filter by user
            if self.user_is_blacklisted(post):
                ids_to_remove.append(post_id)
                continue
            # Filter by keywords
            if self.contains_keyword(post):
                ids_to_remove.append(post_id)
                continue

        # Delete blacklisted posts
        for post_id in ids_to_remove:
            del queue[post_id]

    def contains_keyword(self, post):
        text = preprocess_text(post['full_text'])
        keywords = create_keyword_mutations(*TwitterConfig.get().search.filter.blacklist.keywords)

        for keyword in keywords:
            if count_keyword_in_text(keyword, text) > 0:
                logger.info('Skipping {} because it contains {} keyword'.format(post['id'], keyword))
                return True
        return False

    def user_is_blacklisted(self, post):
        user = post['user']['screen_name'].lower().strip()
        for blacklisted_user in TwitterConfig.get().search.filter.blacklist.users:
            if user == blacklisted_user.lower().strip():
                logger.info('Skipping {} because user {} is blacklisted'.format(post['id'], user))
                return True
        return False

    @staticmethod
    def is_enabled():
        return TwitterConfig.get().search.filter.blacklist.enabled

    @staticmethod
    def get_config_template():
        # Fixme: minor hack because StrSeq doesnt support default
        strseq = confuse.StrSeq()
        strseq.default = []
        template = {
            'enabled': confuse.TypeTemplate(bool),
            'keywords': strseq,
            'users': strseq,
        }
        return template
