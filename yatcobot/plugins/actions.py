import logging
import random
from abc import abstractmethod
from itertools import product

import confuse

from yatcobot.config import TwitterConfig
from yatcobot.config.templates import NumberKeywordsTemplate
from yatcobot.plugins import PluginABC, MergeAllSubclassesConfigsMixin, GetEnabledSubclassesMixin
from yatcobot.utils import create_keyword_mutations, preprocess_text

logger = logging.getLogger(__name__)


class ActionABC(MergeAllSubclassesConfigsMixin, GetEnabledSubclassesMixin, PluginABC):

    def __init__(self, client):
        self.client = client

    @abstractmethod
    def process(self, post):
        """Action must implement process"""


class Follow(ActionABC):
    """
    Checks if a contest needs follow to enter and follows the user

    """

    name = 'follow'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if TwitterConfig.get().actions.follow.multiple:
            logger.warning('Experimental feature actions.follow.multiple is enabled.')
            logger.warning('Will follow every mentioned user in a post.')
            logger.warning('If unwanted behavior is observed, please open an issue on github along with the post id!')

    def process(self, post):
        text = preprocess_text(post['full_text'])
        keywords = create_keyword_mutations(*TwitterConfig.get().actions.follow.keywords)
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

    @staticmethod
    def is_enabled():
        return TwitterConfig.get().actions.follow.enabled

    @staticmethod
    def get_config_template():
        template = {
            'enabled': confuse.TypeTemplate(bool),
            'keywords': confuse.StrSeq(),
            'max_following': confuse.Integer(),
            'multiple': confuse.TypeTemplate(bool)
        }
        return template


class Favorite(ActionABC):
    """
    Checks if a contest needs favorite to enter, and favorites the post
    """

    name = 'favorite'

    def process(self, post):
        text = preprocess_text(post['full_text'])
        keywords = create_keyword_mutations(*TwitterConfig.get().actions.favorite.keywords)
        if any(x in text.lower() for x in keywords):
            r = self.client.favorite(post['id'])
            logger.info("Favorite: {0}".format(post['id']))

    @staticmethod
    def is_enabled():
        return TwitterConfig.get().actions.favorite.enabled

    @staticmethod
    def get_config_template():
        template = {
            'enabled': confuse.TypeTemplate(bool),
            'keywords': confuse.StrSeq()
        }
        return template


class TagFriend(ActionABC):
    """
    Tag one ore more friends in the comments
    """

    name = 'tag_friend'

    class NotEnoughFriends(Exception):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if TwitterConfig.get().actions.tag_friend.enabled:
            logger.warning('Experimental feature actions.tag_friend is enabled.')
            logger.warning('If unwanted behavior is observed, please open an issue on github along with the post id!')

    def process(self, post):
        if not self.tag_needed(post):
            return
        try:
            number = self.get_friends_required(post)
            self.tag_friends(post, number)
        except ValueError:
            logger.error('Error tagging friend for post {}. Please please open an issue with this message on github'
                         .format(post['id']))
        except TagFriend.NotEnoughFriends:
            logger.error('Not enough friends are defined for tagging on post: {}, {} are needed. Define more friends'
                         .format(post['id'], number))

    def tag_needed(self, post):
        text = preprocess_text(post['full_text'])

        tag_keywords = create_keyword_mutations(*TwitterConfig.get().actions.tag_friend.tag_keywords)
        if not any(x in text for x in tag_keywords):
            return False

        friend_keywords = create_keyword_mutations(*TwitterConfig.get().actions.tag_friend.friend_keywords)
        if not any(x in text for x in friend_keywords):
            return False

        return True

    def get_friends_required(self, post):
        text = preprocess_text(post['full_text'])

        # Create keyword mutations
        tag_keywords = create_keyword_mutations(*TwitterConfig.get().actions.tag_friend.tag_keywords)
        friend_keywords = create_keyword_mutations(*TwitterConfig.get().actions.tag_friend.friend_keywords)

        # Find all occurrences of the keywords
        tag_keywords_found = sorted(set(i for x in tag_keywords for i in self.find_all(x, text)))
        friend_keywords_found = sorted(set(i for x in friend_keywords for i in self.find_all(x, text)))

        # Remove indexes of friend keyword that are before any tag keyword
        friend_keywords_found = [x for x in friend_keywords_found if x > min(tag_keywords_found)]

        # Create all combinations between occurrences
        indexes = list(product(tag_keywords_found, friend_keywords_found))

        # Find where the two keywords are closest
        closest_pair = [x for x in sorted(indexes, key=lambda x: x[1] - x[0]) if x[1] - x[0] > 0]
        if len(closest_pair) == 0:
            raise ValueError("Could not find substring")

        closest_pair = closest_pair[0]

        substring = text[closest_pair[0]: closest_pair[1]]

        # Split substring to words and remove empty
        substring = list(filter(None, substring.split(' ')))

        if len(substring) != 2:
            raise ValueError('Could not find how many tag are needed')

        amount = substring[1]

        for number, keywords in TwitterConfig.get().actions.tag_friend.number_keywords.items():
            if amount in keywords:
                return number

        raise ValueError('Could not determinate how many tags are needed')

    def tag_friends(self, post, number):

        if len(TwitterConfig.get().actions.tag_friend.friends) < number:
            raise TagFriend.NotEnoughFriends('Not enough friends')

        # Copy friends list
        friends = list(TwitterConfig.get().actions.tag_friend.friends)

        # Randomize order
        random.shuffle(friends)

        text = '@{}\n'.format(post['user']['screen_name'])

        for friend in friends[:number]:
            text += '@{} '.format(friend)

        logger.info('Responding to {} with text:{}'.format(post['id'], text.replace('\n', ' ')))
        self.client.update(text, post['id'])

    def find_all(self, p, s):
        """Yields all the positions of
        the pattern p in the string s."""
        i = s.find(p)
        while i != -1:
            yield i
            i = s.find(p, i + 1)

    @staticmethod
    def is_enabled():
        return TwitterConfig.get().actions.tag_friend.enabled

    @staticmethod
    def get_config_template():

        template = {
            'enabled': confuse.TypeTemplate(bool),
            'friends': confuse.StrSeq(),
            'tag_keywords': confuse.StrSeq(),
            'friend_keywords': confuse.StrSeq(),
            'number_keywords': NumberKeywordsTemplate()
        }
        return template
