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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if TwitterConfig.get().actions.follow.multiple:
            logger.warning('Experimental feature actions.follow.multiple is enabled.')
            logger.warning('Will follow every mentioned user in a post.')
            logger.warning('If unwanted behavior is observed, please open an issue on github along with the post id!')

    def process(self, post):
        text = post['full_text']
        keywords = sum((create_keyword_mutations(x) for x in TwitterConfig.get().actions.follow.keywords), [])
        if any(x in text.lower() for x in keywords):
            self.remove_oldest_follow()
            self.follow(post)

    def remove_oldest_follow(self):
        """
        If the follow limit is reached, unfollow the oldest follow
        """

        follows = self.client.get_friends_ids()

        if len(follows) > TwitterConfig.get().actions.follow.max_following:
            r = self.client.unfollow(follows[-1])
            logger.info('Unfollowed: {0}'.format(r['screen_name']))

    def follow(self, post):
        users_followed = list()

        # If multiple users is enabled follow all users mentioned
        if TwitterConfig.get().actions.follow.multiple:
            for user in post['entities']['user_mentions']:
                self.client.follow(user['screen_name'])
                users_followed.append(user['screen_name'])
                logger.info("Follow: {0}".format(user['screen_name']))

        # If op not already followed, follow
        if post['user']['screen_name'] not in users_followed:
            self.client.follow(post['user']['screen_name'])
            logger.info("Follow: {0}".format(post['user']['screen_name']))


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
