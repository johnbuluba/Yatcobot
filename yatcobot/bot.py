from collections import OrderedDict
import difflib
import logging


from .scheduler import PeriodicScheduler
from .config import Config
from .ignorelist import IgnoreList
from .client import TwitterClient, TwitterClientRetweetedException
from .post_queue_sort import post_queue_sort
#The logger object
logger = logging.getLogger(__name__)


class Yatcobot():

    def __init__(self, ignore_list_file):

        self.ignore_list = IgnoreList(ignore_list_file)
        self.post_queue = OrderedDict()
        self.client = TwitterClient(Config.consumer_key, Config.consumer_secret,
                                                         Config.access_token_key,
                                                         Config.access_token_secret)
        self.scheduler = PeriodicScheduler()

    def enter_contest(self):
        """ Gets one post from post_queue and retweets it"""

        logger.info("=== CHECKING RETWEET QUEUE ===")

        logger.info("Queue length: {}".format(len(self.post_queue)))

        if len(self.post_queue) > 0:

            post_id, post = self.post_queue.popitem(last=False)

            text = post['text'].replace('\n', '')
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

            self.check_for_follow(post)
            self.check_for_favorite(post)

    def check_for_follow(self, post):
        """
        Checks if a contest needs follow to enter and follows the user
        :param post: The post to check
        """

        text = post['text']
        keywords = sum((self._get_keyword_mutations(x) for x in Config.follow_keywords), [])
        if any(x in text.lower() for x in keywords):
            self.remove_oldest_follow()
            self.client.follow(post['user']['screen_name'])
            logger.info("Follow: {0}".format(post['user']['screen_name']))

    def check_for_favorite(self, post):
        """
        Checks if a contest needs favorite to enter, and favorites the post
        :param post: The post to check
        """

        text = post['text']
        keywords = sum((self._get_keyword_mutations(x) for x in Config.fav_keywords), [])
        if any(x in text.lower() for x in keywords):
            r = self.client.favorite(post['id'])
            logger.info("Favorite: {0}".format(post['id']))

    def remove_oldest_follow(self):
        """
        If the follow limit is reached, unfollow the oldest follow
        """

        follows = self.client.get_friends_ids()

        if len(follows) > Config.max_follows:
            r = self.client.unfollow(follows[-1])
            logger.info('Unfollowed: {0}'.format(r['screen_name']))

    def clear_queue(self):
        """Removes the extraneous posts from the post_queue"""

        to_delete = len(self.post_queue) - Config.max_queue

        if to_delete > 0:
            for i in range(to_delete):
                #Remove from the end where the posts has lower score
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

        for search_query in Config.search_queries:

            results = self.client.search_tweets(search_query, 50)
            logger.info("Got {} new results for: {}".format(len(results), search_query))

            for post in results:
                self._insert_post_to_queue(post)

        #Sort the queue based on some features
        self.post_queue = post_queue_sort(self.post_queue)

    def run(self):
        """Run the bot as a daemon. This is blocking command"""

        self.scheduler.enter(Config.clear_queue_interval, 1, self.clear_queue)
        self.scheduler.enter(Config.rate_limit_update_interval, 2, self.client.update_ratelimits)
        self.scheduler.enter(Config.blocked_users_update_interval, 3, self.update_blocked_users)
        self.scheduler.enter(Config.scan_interval, 4, self.scan_new_contests)
        self.scheduler.enter_random(Config.retweet_interval, Config.retweet_random_margin, 5, self.enter_contest)

        #Init the program
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
        :param post: The post to check if its a quote
        :return: If it isnt a quote the argument, otherwise the original tweet
        """
        if 'quoted_status' not in post:
            return post

        quote = post['quoted_status']

        diff = difflib.SequenceMatcher(None, post['text'], quote['text']).ratio()

        if diff >= Config.min_quote_similarity:
            logger.debug('Tweet {} is a quote'.format(post['id']))
            quote = self.client.get_tweet(post['id'])
            return quote

        return post

    def _insert_post_to_queue(self, post):
        """
        Check if a post is wanted and add's it in the post queue
        :param post: The post to insert
        """
        #Get original tweet if retweeted
        post = self._get_original_tweet(post)

        #Get original post, if it is quoted
        post = self._get_quoted_tweet(post)

        #Filter retweeted
        if post['retweeted']:
            return

        #Filter ids in ignore list
        if post['id'] in self.ignore_list:
            return

        #Insert if it doenst already exists
        if post['id'] not in self.post_queue:
            self.post_queue[post['id']] = post
            text = post['text'].replace('\n', '')
            text = (text[:75] + '..') if len(text) > 75 else text
            logger.debug("Added tweet to queue: id:{0} username:{1} text:{2}".format(post['id'],
                                                                                     post['user']['screen_name'],
                                                                                     text))

    def _get_keyword_mutations(self, keyword):
        """
        Given a keyword, create various mutations to be searched inside a post
        :param keyword: the base keyword of the mutations
        :return: list of mutation
        """
        mutations = list()
        keyword = keyword.strip()
        mutations.append(' {} '.format(keyword))
        mutations.append('{} '.format(keyword))
        mutations.append(' {}'.format(keyword))
        mutations.append('#{}'.format(keyword))
        mutations.append(',{}'.format(keyword))
        mutations.append('{},'.format(keyword))
        mutations.append('.{}'.format(keyword))
        mutations.append('{}.'.format(keyword))
        return mutations