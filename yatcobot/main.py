import logging
import time
import sys

from TwitterAPI import TwitterAPI


from .scheduler import PeriodicScheduler
from .config import Config
import yatcobot.client

#The logger object
logger = logging.getLogger(__name__)


client = None


# Don't edit these unless you know what you're doing.
api = None #Its initialized if this is main
post_list = list()


class IgnoreList(list):
    """
    A list like object that loads contents from a file and everything that is appended here gets also
    appended in the file
    """

    def __init__(self, filename):
        self.filename = filename
        self.load_file()

    def append(self, p_object):
        self.append_file(p_object)
        super().append(p_object)

    def load_file(self):
        with open(self.filename, 'a+') as f:
            f.seek(0)
            self.extend(int(x) for x in f.read().splitlines())

    def append_file(self, p_object):
        with open(self.filename, 'a+') as f:
            f.write(str(p_object) + '\n')


ignore_list = None


def UpdateQueue():
    """ Update the Retweet queue (this prevents too many retweets happening at once.)"""

    logger.info("=== CHECKING RETWEET QUEUE ===")

    logger.info("Queue length: {}".format(len(post_list)))

    if len(post_list) > 0:

        post = post_list.pop(0)

        logger.info("Retweeting: {0} {1}".format(post['id'], post['text'].encode('utf8')))

        r = client.get_tweet(post['id'])

        user_item = r['user']
        user_id = user_item['id']

        if user_id in ignore_list:
            logger.info("Blocked user's tweet skipped")
            return

        r = client.retweet(post['id'])

        CheckForFollowRequest(post)
        CheckForFavoriteRequest(post)


def CheckForFollowRequest(item):
    """
    Check if a post requires you to follow the user.
    Be careful with this function! Twitter may write ban your application
    for following too aggressively
    """
    #!Fixme doesnt find .Follow, #Follow

    text = item['text']
    if any(x in text.lower() for x in Config.follow_keywords):
        RemoveOldestFollow()
        try:
            r = client.follow(item['retweeted_status']['user']['screen_name'])
            logger.info("Follow: {0}".format(item['retweeted_status']['user']['screen_name']))
        except:
            user = item['user']
            screen_name = user['screen_name']
            r = client.follow(screen_name)
            logger.info("Follow: {0}".format(screen_name))


def RemoveOldestFollow():
    """FIFO - Every new follow should result in the oldest follow being removed."""

    friends = list()
    for id in client.get_friends_ids():
        friends.append(id)

    oldest_friend = friends[-1]

    if len(friends) > Config.max_follows:

        r = client.unfollow(oldest_friend)
        logger.info('Unfollowed: {0}'.format(r['screen_name']))

    else:
        logger.info("No friends unfollowed")


def CheckForFavoriteRequest(item):
    """
    Check if a post requires you to favorite the tweet.
    Be careful with this function! Twitter may write ban your application
    for favoriting too aggressively

    """
    text = item['text']

    if any(x in text.lower() for x in Config.fav_keywords):
        try:
            r = client.favorite(item['retweeted_status']['id'])
            logger.info("Favorite: {0}".format(item['retweeted_status']['id']))
        except:
            r = client.favorite(item['id'])
            logger.info("Favorite: {0}".format(item['id']))


def ClearQueue():
    """Clear the post list queue in order to avoid a buildup of old posts"""

    post_list_length = len(post_list)

    if post_list_length > Config.min_posts_queue:
        del post_list[:post_list_length - Config.min_posts_queue]
        logger.info("===THE QUEUE HAS BEEN CLEARED===")


def CheckBlockedUsers():

    for b in client.get_blocks():
        if not b in ignore_list:
            ignore_list.append(b)
            logger.info("Blocked user {0} added to ignore list".format(b))


def ScanForContests():
    """Scan for new contests, but not too often because of the rate limit."""

    logger.info("=== SCANNING FOR NEW CONTESTS ===")

    for search_query in Config.search_queries:

        logger.info("Getting new results for: {0}".format(search_query))

        try:
            r = client.search_tweets(search_query, 50)
            c = 0

            for item in r:
                c += 1
                user_item = item['user']
                screen_name = user_item['screen_name']
                text = item['text']
                text = text.replace("\n", "")
                id = item['id']
                original_id = id

                if 'retweeted_status' in item:

                    original_item = item['retweeted_status']
                    original_id = original_item['id']
                    original_user_item = original_item['user']
                    original_screen_name = original_user_item['screen_name']

                    if original_id in ignore_list:
                        logger.debug("{0} ignored {1} in ignore list".format(id, original_id))
                        continue

                    if original_user_item['id'] in ignore_list:
                        logger.info("{0} ignored {1} blocked and in ignore list".format(id, original_screen_name))
                        continue

                    post_list.append(original_item)

                    logger.info("{0} - {1} retweeting {2} - {3} : {4}".format(id, screen_name, original_id,
                                                                              original_screen_name, text))

                    ignore_list.append(original_id)

                else:

                    if id in ignore_list:
                        logger.debug("{0} in ignore list".format(id))
                        continue

                    if user_item['id'] in ignore_list:
                        logger.info("{0} ignored {1} blocked user in ignore list".format(id, screen_name))
                        continue

                    post_list.append(item)

                    logger.debug("{0} - {1} : {2}".format(id, screen_name, text))
                    ignore_list.append(id)

            logger.info("Got {0} results".format(c))

        except Exception as e:
            logger.exception("Could not connect to TwitterAPI - are your credentials correct?")


def run():
    #Load config
    Config.load('config.json')
    global client, ignore_list, api

    #Initialize twitter api
    api = TwitterAPI(
        Config.consumer_key,
        Config.consumer_secret,
        Config.access_token_key,
        Config.access_token_secret)

    client = yatcobot.client.TwitterClient(Config.consumer_key,
                            Config.consumer_secret,
                            Config.access_token_key,
                            Config.access_token_secret)

    client.update_ratelimits()
    #Initialize ignorelist
    ignore_list = IgnoreList("ignorelist")

    #Initialize Scheduler
    s = PeriodicScheduler()

    s.enter(Config.clear_queue_time, 1, ClearQueue)
    s.enter(Config.rate_limit_update_time, 2, client.update_ratelimits)
    s.enter(Config.blocked_users_update_time, 3, CheckBlockedUsers)
    s.enter(Config.scan_update_time, 4, ScanForContests)
    s.enter_random(Config.retweet_update_time, Config.retweet_random_margin, 5, UpdateQueue)

    #Init the program
    s.run()



