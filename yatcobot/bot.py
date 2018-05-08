import difflib
import logging
from collections import OrderedDict

from yatcobot.plugins.actions import ActionABC
from .client import TwitterClient, TwitterClientRetweetedException
from .config import TwitterConfig
from .ignorelist import IgnoreList
from .notifier import NotificationService
from .post_queue import PostQueue
from .scheduler import PeriodicScheduler

# The logger object
logger = logging.getLogger(__name__)


class Yatcobot:

    def __init__(self, ignore_list_file):

        self.ignore_list = IgnoreList(ignore_list_file)
        self.post_queue = PostQueue()
        self.client = TwitterClient(TwitterConfig.get()['consumer_key'],
                                    TwitterConfig.get()['consumer_secret'],
                                    TwitterConfig.get()['access_token_key'],
                                    TwitterConfig.get()['access_token_secret'])
        self.scheduler = PeriodicScheduler()
        self.notification = NotificationService()

        self.actions = ActionABC.get_enabled(self.client)

        self.last_mention = None

    def enter_contest(self):
        """ Gets one post from post_queue and retweets it"""

        logger.info("=== CHECKING RETWEET QUEUE ===")

        logger.info("Queue length: {}".format(len(self.post_queue)))

        while True:
            post = self.post_queue.get()
            score = post['score']
            # Get post to refresh retweeted value
            post = self.client.get_tweet(post['id'])
            post['score'] = score

            # If post not retweeted retweet
            if not post['retweeted']:
                break

            # Post already retweeted save it to ignore list
            self.ignore_list.append(post['id'])

            # If skip enabled, get next post from queue
            if TwitterConfig.get().search.skip_retweeted:
                logger.info('Skipping already retweeted post with id {}'.format(post_id))
                continue

            logger.error("Alredy retweeted tweet with id {}".format(post['id']))
            return

        text = post['full_text'].replace('\n', '')
        text = (text[:75] + '..') if len(text) > 75 else text
        logger.info("Retweeting: {0} {1}".format(post['id'], text))
        logger.debug("Tweet score: {}".format(post['score']))

        if post['user']['id'] in self.ignore_list:
            logger.info("Blocked user's tweet skipped")
            return
        try:
            self.client.retweet(post['id'])
            self.ignore_list.append(post['id'])

        except TwitterClientRetweetedException:
            self.ignore_list.append(post['id'])
            logger.error("Alredy retweeted tweet with id {}".format(post['id']))
            return

        for action in self.actions:
            action.process(post)

    def clear_queue(self):
        """Removes the extraneous posts from the post_queue"""

        to_delete = len(self.post_queue) - TwitterConfig.get().search.max_queue

        if to_delete > 0:
            for i in range(to_delete):
                # Remove from the end where the posts has lower score
                self.post_queue.popitem()

            logger.info("===THE QUEUE HAS BEEN CLEARED=== Deleted {} posts".format(to_delete))

    def update_blocked_users(self):
        """Gets the blocked users and adds their ids in the ignore list"""

        for b in self.client.get_blocks():
            if not b in self.ignore_list:
                self.ignore_list.append(b)
                logger.info("Blocked user {0} added to ignore list".format(b))

    def check_new_mentions(self):
        """
        Check if someone mentioned the user and sends a notification
        Usefull because many winners are mentioned in tweets
        """

        # Check if notification is enabled
        if not self.notification.is_enabled():
            return

        # If its the first time its called get the last mention
        logger.info("=== CHECKING NEW MENTIONS ===")
        if self.last_mention is None:
            posts = self.client.get_mentions_timeline(count=1)
            if len(posts) > 0:
                self.last_mention = posts[0]
            return

        # Else check if there are new mentions after the last, notify
        posts = self.client.get_mentions_timeline(since_id=self.last_mention['id'])
        if len(posts) > 0:
            links = ' , '.join(self.create_tweet_link(x) for x in posts)
            logger.info("You ve got {} new mentions: {}".format(len(posts), links))
            self.notification.send_notification('Yatcobot: Someone mentioned you, you may won something!',
                                                '{} new mentions : \n {}'.format(len(posts), links))

            self.last_mention = posts[0]

    def run(self):
        """Run the bot as a daemon. This is blocking command"""

        self.scheduler.enter(TwitterConfig.get().scheduler.clear_queue_interval, 1, self.clear_queue)
        self.scheduler.enter(TwitterConfig.get().scheduler.rate_limit_update_interval, 2, self.client.update_ratelimits)
        self.scheduler.enter(TwitterConfig.get().scheduler.blocked_users_update_interval, 3, self.update_blocked_users)
        self.scheduler.enter(TwitterConfig.get().scheduler.check_mentions_interval, 4, self.check_new_mentions)
        self.scheduler.enter_random(TwitterConfig.get().scheduler.retweet_interval,
                                    TwitterConfig.get().scheduler.retweet_random_margin, 6, self.enter_contest)

        # Init the program
        self.scheduler.run()

    def create_tweet_link(self, post):
        return "http://twitter.com/{}/status/{}".format(post['user']['screen_name'], post['id'])
