import logging


from .scheduler import PeriodicScheduler
from .config import Config
from .ignorelist import IgnoreList
from .client import TwitterClient, TwitterClientRetweetedException

#The logger object
logger = logging.getLogger(__name__)


class Yatcobot():

    def __init__(self, confg_file, ignore_list_file):

        Config.load(confg_file)

        self.queue = list()
        self.ignore_list = IgnoreList(ignore_list_file)
        self.post_list = list()
        self.client = TwitterClient(Config.consumer_key, Config.consumer_secret,
                                                         Config.access_token_key,
                                                         Config.access_token_secret)
        self.scheduler = PeriodicScheduler()

    def enter_contest(self):
        """ Update the Retweet queue (this prevents too many retweets happening at once.)"""

        logger.info("=== CHECKING RETWEET QUEUE ===")

        logger.info("Queue length: {}".format(len(self.post_list)))

        if len(self.post_list) > 0:

            post = self.post_list.pop(0)

            logger.info("Retweeting: {0} {1}".format(post['id'], post['text'].encode('utf8')))

            r = self.client.get_tweet(post['id'])

            user_item = r['user']
            user_id = user_item['id']

            if user_id in self.ignore_list:
                logger.info("Blocked user's tweet skipped")
                return
            try:
                r = self.client.retweet(post['id'])
            except TwitterClientRetweetedException:
                self.ignore_list.append(post['id'])
                logger.error("Alredy retweeted tweet with id {}".format(post['id']))
                return

            self.check_follow_request(post)
            self.check_for_favorite(post)

    def check_follow_request(self, item):
        """
        Check if a post requires you to follow the user.
        Be careful with this function! Twitter may write ban your application
        for following too aggressively
        """
        #!Fixme doesnt find .Follow, #Follow

        text = item['text']
        if any(x in text.lower() for x in Config.follow_keywords):
            self.remove_oldest_follow()
            try:
                r = self.client.follow(item['retweeted_status']['user']['screen_name'])
                logger.info("Follow: {0}".format(item['retweeted_status']['user']['screen_name']))
            except:
                user = item['user']
                screen_name = user['screen_name']
                r = self.client.follow(screen_name)
                logger.info("Follow: {0}".format(screen_name))

    def remove_oldest_follow(self):
        """FIFO - Every new follow should result in the oldest follow being removed."""

        friends = list()
        for id in self.client.get_friends_ids():
            friends.append(id)

        oldest_friend = friends[-1]

        if len(friends) > Config.max_follows:

            r = self.client.unfollow(oldest_friend)
            logger.info('Unfollowed: {0}'.format(r['screen_name']))

        else:
            logger.info("No friends unfollowed")

    def check_for_favorite(self, item):
        """
        Check if a post requires you to favorite the tweet.
        Be careful with this function! Twitter may write ban your application
        for favoriting too aggressively

        """
        text = item['text']

        if any(x in text.lower() for x in Config.fav_keywords):
            try:
                r = self.client.favorite(item['retweeted_status']['id'])
                logger.info("Favorite: {0}".format(item['retweeted_status']['id']))
            except:
                r = self.client.favorite(item['id'])
                logger.info("Favorite: {0}".format(item['id']))

    def clear_queue(self):
        """Clear the post list queue in order to avoid a buildup of old posts"""

        post_list_length = len(self.post_list)

        if post_list_length > Config.min_posts_queue:
            del self.post_list[:post_list_length - Config.min_posts_queue]
            logger.info("===THE QUEUE HAS BEEN CLEARED===")

    def update_blocked_users(self):

        for b in self.client.get_blocks():
            if not b in self.ignore_list:
                self.ignore_list.append(b)
                logger.info("Blocked user {0} added to ignore list".format(b))

    def scan_new_contests(self):
        """Scan for new contests, but not too often because of the rate limit."""

        logger.info("=== SCANNING FOR NEW CONTESTS ===")

        for search_query in Config.search_queries:

            logger.info("Getting new results for: {0}".format(search_query))

            r = self.client.search_tweets(search_query, 50)
            c = 0

            for item in r:
                c += 1
                user_item = item['user']
                screen_name = user_item['screen_name']
                text = item['text']
                text = text.replace("\n", "")
                id = item['id']

                if 'retweeted_status' in item:

                    original_item = item['retweeted_status']
                    original_id = original_item['id']
                    original_user_item = original_item['user']
                    original_screen_name = original_user_item['screen_name']

                    if original_id in self.ignore_list:
                        logger.debug("{0} ignored {1} in ignore list".format(id, original_id))
                        continue

                    if original_user_item['id'] in self.ignore_list:
                        logger.info("{0} ignored {1} blocked and in ignore list".format(id, original_screen_name))
                        continue

                    self.post_list.append(original_item)

                    logger.debug("Got retweet: id:{0} username:{1} original_id:{2} origina_username:{3} text:{4}"
                                 .format(id, screen_name, original_id, original_screen_name, text))

                    self.ignore_list.append(original_id)

                else:

                    if id in self.ignore_list:
                        logger.debug("{0} in ignore list".format(id))
                        continue

                    if user_item['id'] in self.ignore_list:
                        logger.info("{0} ignored {1} blocked user in ignore list".format(id, screen_name))
                        continue

                    self.post_list.append(item)

                    logger.debug("Got tweet: id:{0} username:{1} text:{2}".format(id, screen_name, text))
                    self.ignore_list.append(id)

            logger.info("Got {0} results".format(c))

    def run(self):

        self.scheduler.enter(Config.clear_queue_time, 1, self.clear_queue)
        self.scheduler.enter(Config.rate_limit_update_time, 2, self.client.update_ratelimits)
        self.scheduler.enter(Config.blocked_users_update_time, 3, self.update_blocked_users)
        self.scheduler.enter(Config.scan_update_time, 4, self.scan_new_contests)
        self.scheduler.enter_random(Config.retweet_update_time, Config.retweet_random_margin, 5, self.enter_contest)

        #Init the program
        self.scheduler.run()



