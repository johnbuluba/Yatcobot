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

        while len(self.post_queue) > 0:
            post_id, post = self.post_queue.popitem(last=False)
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
        else:
            logger.warning('Queue empty')
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

    def scan_new_contests(self):
        """Searches the twitter for new contests and adds the to the post queue"""

        logger.info("=== SCANNING FOR NEW CONTESTS ===")

        for search_query in TwitterConfig.get().search.queries:

            if isinstance(search_query, str):
                results = self.client.search_tweets(search_query, 50)
            elif isinstance(search_query, OrderedDict):
                lang = search_query['lang']
                search_query = list(search_query.keys())[0]

                results = self.client.search_tweets(search_query, 50, language=lang)
            else:
                raise ValueError("Uknown type of query {}".format(str(search_query)))

            logger.info("Got {} new results for: {}".format(len(results), search_query))

            for post in results:
                self._insert_post_to_queue(post)

        # Filter queue based on configure filters
        self.post_queue.filter()
        # Sort the queue based on some features
        self.post_queue.sort()

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
        self.scheduler.enter(TwitterConfig.get().scheduler.search_interval, 5, self.scan_new_contests)
        self.scheduler.enter_random(TwitterConfig.get().scheduler.retweet_interval,
                                    TwitterConfig.get().scheduler.retweet_random_margin, 6, self.enter_contest)

        # Init the program
        self.scheduler.run()

    def _get_original_tweet(self, post):
        """
        Checks if a post is a retweet and returns original tweet
        :param post: Post to check if its retweeted
        :return: post: If itsnt retweet it returns the argument, otherwise returns original tweet
        """
        if 'retweeted_status' in post:
            logger.debug('Tweet {} is a retweet'.format(post['id']))
            return post['retweeted_status']
        return post

    def _get_quoted_tweet(self, post):
        """
        Checks if a post is a quote of the original tweet
        Also the quote maybe is quoting another quote. So we follow quotes until we find the original or
        if we follow Config.max_quote_depth times
        :param post: The post to check if its a quote
        :return: If it isnt a quote the argument, otherwise the original tweet
        """
        for i in range(TwitterConfig.get().search.max_quote_depth):
            # If it hasnt quote return the post
            if 'quoted_status' not in post:
                return post

            quote = post['quoted_status']
            diff = difflib.SequenceMatcher(None, post['full_text'], quote['full_text']).ratio()
            # If the texts are similar continue
            if diff >= TwitterConfig.get().search.min_quote_similarity:
                logger.debug('{} is a quote, following to next post. Depth from original post {}'.format(post['id'], i))
                quote = self.client.get_tweet(quote['id'])
                # If its a quote of quote, get next quote and continue
                post = quote
                continue
            # Else return the last post
            break

        return post

    def _insert_post_to_queue(self, post):
        """
        Check if a post is wanted and add's it in the post queue
        :param post: The post to insert
        """
        # Get original tweet if retweeted
        post = self._get_original_tweet(post)

        # Get original post, if it is quoted
        post = self._get_quoted_tweet(post)

        # Filter ids in ignore list
        if post['id'] in self.ignore_list:
            return

        # Filter blocked users
        if post['user']['id'] in self.ignore_list:
            return

        # Filter posts with deleted quote
        # We check if there is a key 'is_a_quote_status' that is true but there isn't a quoted_status
        if 'is_quote_status' in post and post['is_quote_status'] and not 'quoted_status' in post:
            return

        # Insert if it doenst already exists
        if post['id'] not in self.post_queue:
            self.post_queue[post['id']] = post
            text = post['full_text'].replace('\n', '')
            text = (text[:75] + '..') if len(text) > 75 else text
            logger.debug("Added tweet to queue: id:{0} username:{1} text:{2}".format(post['id'],
                                                                                     post['user']['screen_name'],
                                                                                     text))

    def create_tweet_link(self, post):
        return "http://twitter.com/{}/status/{}".format(post['user']['screen_name'], post['id'])
