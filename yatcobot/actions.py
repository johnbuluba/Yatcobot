import logging
from abc import ABC, abstractmethod

from .config import TwitterConfig
from .utils import create_keyword_mutations

logger = logging.getLogger(__name__)


class ActionABC(ABC):

    def __init__(self, client):
        self.client = client

    @abstractmethod
    def process(self, post):
        raise NotImplementedError("Action must implement process")


class Follow(ActionABC):
    """
    Checks if a contest needs follow to enter and follows the user

    """

    def process(self, post):
        text = post['full_text']
        keywords = sum((create_keyword_mutations(x) for x in TwitterConfig.get().actions.follow.keywords), [])
        if any(x in text.lower() for x in keywords):
            self.remove_oldest_follow()
            self.client.follow(post['user']['screen_name'])
            logger.info("Follow: {0}".format(post['user']['screen_name']))

    def remove_oldest_follow(self):
        """
        If the follow limit is reached, unfollow the oldest follow
        """

        follows = self.client.get_friends_ids()

        if len(follows) > TwitterConfig.get().actions.follow.max_following:
            r = self.client.unfollow(follows[-1])
            logger.info('Unfollowed: {0}'.format(r['screen_name']))


class Favorite(ActionABC):
    """
    Checks if a contest needs favorite to enter, and favorites the post
    """

    def process(self, post):
        text = post['full_text']
        keywords = sum((create_keyword_mutations(x) for x in TwitterConfig.get().actions.favorite.keywords), [])
        if any(x in text.lower() for x in keywords):
            r = self.client.favorite(post['id'])
            logger.info("Favorite: {0}".format(post['id']))
