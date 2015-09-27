from TwitterAPI import TwitterAPI
import sched
import logging
import time
import json
import sys
from collections import namedtuple
import random


def get_logger():
    """Creates the logger object that is used for logging in the file"""

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    #Create log outputs
    fh = logging.FileHandler('log')
    ch = logging.StreamHandler()

    #Log format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    #Set logging format
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    #Set level per output
    fh.setLevel(logging.DEBUG)
    ch.setLevel(logging.INFO)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


#The logger object
logger = get_logger()


class Config:
    """Class that contains all  config variables. It loads user values from a json file """

    # Default values
    consumer_key = None
    consumer_secret = None
    access_token_key = None
    access_token_secret = None
    retweet_update_time = 600
    retweet_random_margin = 60
    scan_update_time = 5400
    clear_queue_time = 43200
    min_posts_queue = 60
    rate_limit_update_time = 60
    blocked_users_update_time = 300
    min_ratelimit = 10
    min_ratelimit_retweet = 20
    min_ratelimit_search = 40
    max_follows = 1950
    search_queries = ["RT to win", "Retweet and win"]
    follow_keywords = [" follow ", " follower "]
    fav_keywords = [" fav ", " favorite "]

    @staticmethod
    def load(filename):
        # Load our configuration from the JSON file.
        with open(filename) as data_file:
            data = json.load(data_file)

        for key, value in data.items():
            #!Fixme:
            #Hacky code because the corresponding keys in config file use - instead of _
            key = key.replace('-', '_')
            setattr(Config, key, value)


# Don't edit these unless you know what you're doing.
api = None #Its initialized if this is main
post_list = list()
ratelimit = [999, 999, 100]
ratelimit_search = [999, 999, 100]


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


def CheckError(r):
    r = r.json()
    if 'errors' in r:
        logger.error("We got an error message: {0} Code: {1})".format(r['errors'][0]['message'],
                                                                      r['errors'][0]['code']))


def CheckRateLimit():

    global ratelimit
    global ratelimit_search

    if ratelimit[2] < Config.min_ratelimit:
        logger.warn("Ratelimit too low -> Cooldown ({}%)".format(ratelimit[2]))
        time.sleep(30)

    r = api.request('application/rate_limit_status').json()

    for res_family in r['resources']:
        for res in r['resources'][res_family]:
            limit = r['resources'][res_family][res]['limit']
            remaining = r['resources'][res_family][res]['remaining']
            percent = float(remaining) / float(limit) * 100

            if res == "/search/tweets":
                ratelimit_search = [limit, remaining, percent]

            if res == "/application/rate_limit_status":
                ratelimit = [limit, remaining, percent]

            if percent < 5.0:
                message = "{0} Rate Limit-> {1}: {2} !!! <5% Emergency exit !!!".format(res_family, res, percent)
                logger.critical(message)
                sys.exit(message)
            elif percent < 30.0:
                logger.warn("{0} Rate Limit-> {1}: {2} !!! <30% alert !!!".format(res_family, res, percent))
            elif percent < 70.0:
                logger.info("{0} Rate Limit-> {1}: {2}".format(res_family, res, percent))


def UpdateQueue():
    """ Update the Retweet queue (this prevents too many retweets happening at once.)"""

    logger.info("=== CHECKING RETWEET QUEUE ===")

    logger.info("Queue length: {}".format(len(post_list)))

    if len(post_list) > 0:

        if ratelimit[2] < Config.min_ratelimit_retweet:
            logger.info("Ratelimit at {0}% -> pausing retweets".format(ratelimit[2]))
            return

        post = post_list[0]

        if 'errors' in post:
            post_list.pop(0)
            logger.error("We got an error message: {0} Code: {1}".format(post['errors'][0]['message'],
                                                                         post['errors'][0]['code']))
            return

        logger.info("Retweeting: {0} {1}".format(post['id'], post['text'].encode('utf8')))

        r = api.request('statuses/show/:%d' % post['id']).json()
        if 'errors' in r:
            logger.error("We got an error message: {0} Code: {1}".format(r['errors'][0]['message'],
                                                                         r['errors'][0]['code']))
            post_list.pop(0)
            return

        user_item = r['user']
        user_id = user_item['id']

        if user_id in ignore_list:
            post_list.pop(0)
            logger.info("Blocked user's tweet skipped")
            return

        r = api.request('statuses/retweet/:{0}'.format(post['id']))

        CheckError(r)
        post_list.pop(0)

        if not 'errors' in r.json():

            CheckForFollowRequest(post)
            CheckForFavoriteRequest(post)


def CheckForFollowRequest(item):
    """
    Check if a post requires you to follow the user.
    Be careful with this function! Twitter may write ban your application
    for following too aggressively
    """
    text = item['text']
    if any(x in text.lower() for x in Config.follow_keywords):
        RemoveOldestFollow()
        try:
            r = api.request('friendships/create', {'screen_name': item['retweeted_status']['user']['screen_name']})
            CheckError(r)
            logger.info("Follow: {0}".format(item['retweeted_status']['user']['screen_name']))
        except:
            user = item['user']
            screen_name = user['screen_name']
            r = api.request('friendships/create', {'screen_name': screen_name})
            CheckError(r)
            logger.info("Follow: {0}".format(screen_name))


def RemoveOldestFollow():
    """FIFO - Every new follow should result in the oldest follow being removed."""

    friends = list()
    for id in api.request('friends/ids'):
        friends.append(id)

    oldest_friend = friends[-1]

    if len(friends) > Config.max_follows:

        r = api.request('friendships/destroy', {'user_id': oldest_friend})

        if r.status_code == 200:
            status = r.json()
            logger.info('Unfollowed: {0}'.format(status['screen_name']))

    else:
        logger.info("No friends unfollowed")

    del friends
    del oldest_friend


def CheckForFavoriteRequest(item):
    """
    Check if a post requires you to favorite the tweet.
    Be careful with this function! Twitter may write ban your application
    for favoriting too aggressively

    """
    text = item['text']

    if any(x in text.lower() for x in Config.fav_keywords):
        try:
            r = api.request('favorites/create', {'id': item['retweeted_status']['id']})
            CheckError(r)
            logger.info("Favorite: {0}".format(item['retweeted_status']['id']))
        except:
            r = api.request('favorites/create', {'id': item['id']})
            CheckError(r)
            logger.info("Favorite: {0}".format(item['id']))


def ClearQueue():
    """Clear the post list queue in order to avoid a buildup of old posts"""

    post_list_length = len(post_list)

    if post_list_length > Config.min_posts_queue:
        del post_list[:post_list_length - Config.min_posts_queue]
        logger.info("===THE QUEUE HAS BEEN CLEARED===")


def CheckBlockedUsers():
    """Check list of blocked users and add to ignore list"""
    if ratelimit_search[2] < Config.min_ratelimit_search:
        logger.warn("Update blocked users skipped! Queue: {0} Ratelimit: {1}/{2} ({3}%)".format(len(post_list),
                                                                                                ratelimit_search[1],
                                                                                                ratelimit_search[0],
                                                                                                ratelimit_search[2]))
        return

    for b in api.request('blocks/ids'):
        if not b in ignore_list:
            ignore_list.append(b)
            logger.info("Blocked user {0} added to ignore list".format(b))


def ScanForContests():
    """Scan for new contests, but not too often because of the rate limit."""

    global ratelimit_search

    if ratelimit_search[2] < Config.min_ratelimit_search:

        logger.warn("Search skipped! Queue: {0} Ratelimit: {1}/{2} ({3}%)".format(len(post_list),
                                                                                  ratelimit_search[1],
                                                                                  ratelimit_search[0],
                                                                                  ratelimit_search[2]))
        return

    logger.info("=== SCANNING FOR NEW CONTESTS ===")

    for search_query in Config.search_queries:

        logger.info("Getting new results for: {0}".format(search_query))

        try:
            r = api.request( 'search/tweets', {'q': search_query, 'result_type': "mixed", 'count': 50})
            CheckError(r)
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


class PeriodicScheduler(sched.scheduler):
    """Schedules tasks to be called periodically"""

    #Task types
    NormalTask = namedtuple('NormalTask', ['delay', 'priority', 'action'])
    RandomTask = namedtuple('RandomTask', ['delay', 'delay_margin', 'priority', 'action'])

    def __init__(self, timefunc=time.time, delayfunc=time.sleep):
        # List of tasks that will be periodically be called
        self.tasks = []
        super().__init__(timefunc, delayfunc)

    def enter(self, delay, priority, action):
        """Inserts a new task in the scheduler. Tasks will be called regularly with period delay"""

        task = self.NormalTask(delay, priority, action)
        self.tasks.append(task)

    def enter_random(self, delay, delay_margin, priority, action):
        """
        Inserts a new random task in the scheduler. Tasks will be paused for random time
        from delay-delay_margin to delay+delay_margin
        """
        task = self.RandomTask(delay, delay_margin, priority, action)
        self.tasks.append(task)

    def run(self, blocking=True):
        for i in range(len(self.tasks)):
            self.run_task(i)

        super().run(blocking)

    def enter_task(self, index):
        task = self.tasks[index]
        if isinstance(task, self.NormalTask):
            super().enter(task.delay, task.priority, self.run_task, argument=(index,))

        elif isinstance(task, self.RandomTask):
            delay = random.randint(task.delay- task.delay_margin, task.delay + task.delay_margin)
            super().enter(delay, task.priority, self.run_task, argument=(index,))

    def run_task(self, index):
        self.enter_task(index)
        try:
            logger.debug("Scheduler is calling: {}".format(self.tasks[index][2].__name__))
            self.tasks[index].action()
        except Exception as e:
            logger.error("Exception in scheduled task :{}".format(e))


if __name__ == '__main__':
    #Load config
    Config.load('config.json')

    #Initialize twitter api
    api = TwitterAPI(
        Config.consumer_key,
        Config.consumer_secret,
        Config.access_token_key,
        Config.access_token_secret)

    #Initialize ignorelist
    ignore_list = IgnoreList("ignorelist")

    #Initialize Scheduler
    s = PeriodicScheduler()

    s.enter(Config.clear_queue_time, 1, ClearQueue)
    s.enter(Config.rate_limit_update_time, 2, CheckRateLimit)
    s.enter(Config.blocked_users_update_time, 3, CheckBlockedUsers)
    s.enter(Config.scan_update_time, 4, ScanForContests)
    s.enter_random(Config.retweet_update_time, Config.retweet_random_margin, 5, UpdateQueue)

    #Init the program
    s.run()
