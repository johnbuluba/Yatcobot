import difflib
import logging
from sched import scheduler
from collections import OrderedDict
from threading import Thread

from yatcobot.config import TwitterConfig
from yatcobot.scheduler import PeriodicScheduler

logger = logging.getLogger(__name__)


class ContestSearch(Thread):

    def __init__(self, client, queue, ignore_list):
        super().__init__(name='ContestSearch')
        self.client = client
        self.queue = queue
        self.ignore_list = ignore_list

    def run(self) -> None:
        sched = PeriodicScheduler()
        sched.enter(TwitterConfig.get().scheduler.search_interval, 1, self.scan_new_contests)
        sched.run()

    def scan_new_contests(self):
        """Searches the twitter for new contests and adds the to the post queue"""

        # Reschedule
        self.scheduler.enter(TwitterConfig.get().scheduler.search_interval, 1, self.scan_new_contests())

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
        self.queue.filter()
        # Sort the queue based on some features
        self.queue.sort()

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
        if post['id'] not in self.queue:
            self.queue[post['id']] = post
            text = post['full_text'].replace('\n', '')
            text = (text[:75] + '..') if len(text) > 75 else text
            logger.debug("Added tweet to queue: id:{0} username:{1} text:{2}".format(post['id'],
                                                                                     post['user']['screen_name'],
                                                                                     text))
