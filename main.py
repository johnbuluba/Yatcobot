from TwitterAPI import TwitterAPI
import sched
import logging
import time
import json
import sys
import threading

# Load our configuration from the JSON file.
with open('config.json') as data_file:
    data = json.load(data_file)

# These vars are loaded in from config.
consumer_key = data["consumer-key"]
consumer_secret = data["consumer-secret"]
access_token_key = data["access-token-key"]
access_token_secret = data["access-token-secret"]
retweet_update_time = data["retweet-update-time"]
scan_update_time = data["scan-update-time"]
clear_queue_time = data["clear-queue-time"]
min_posts_queue = data["min-posts-queue"]
rate_limit_update_time = data["rate-limit-update-time"]
blocked_users_update_time = data["blocked-users-update-time"]
min_ratelimit = data["min-ratelimit"]
min_ratelimit_retweet = data["min-ratelimit-retweet"]
min_ratelimit_search = data["min-ratelimit-search"]
max_follows = data["max-follows"]
search_queries = data["search-queries"]
follow_keywords = data["follow-keywords"]
fav_keywords = data["fav-keywords"]


def get_logger():
    #Creates the logger object that is used for logging in the file

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


# Don't edit these unless you know what you're doing.
api = TwitterAPI(
    consumer_key,
    consumer_secret,
    access_token_key,
    access_token_secret)
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


ignore_list = IgnoreList("ignorelist")


def CheckError(r):
    r = r.json()
    if 'errors' in r:
        logger.error("We got an error message: {0} Code: {1})".format(r['errors'][0]['message'],
                                                                      r['errors'][0]['code']))
        # sys.exit(r['errors'][0]['code'])


def CheckRateLimit():

    global ratelimit
    global ratelimit_search

    if ratelimit[2] < min_ratelimit:
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

            #print(res_family + " -> " + res + ": " + str(percent))
            if percent < 5.0:
                message = "{0} Rate Limit-> {1}: {2} !!! <5% Emergency exit !!!".format(res_family, res, percent)
                logger.critical(message)
                sys.exit(message)
            elif percent < 30.0:
                logger.warn("{0} Rate Limit-> {1}: {2} !!! <30% alert !!!".format(res_family, res, percent))
            elif percent < 70.0:
                logger.info("{0} Rate Limit-> {1}: {2}".format(res_family, res, percent))

# Update the Retweet queue (this prevents too many retweets happening at once.)


def UpdateQueue():

    logger.info("=== CHECKING RETWEET QUEUE ===")

    logger.info("Queue length: {}".format(len(post_list)))

    if len(post_list) > 0:

        if not ratelimit[2] < min_ratelimit_retweet:

            post = post_list[0]
            if not 'errors' in post:
                logger.info("Retweeting: {0} {1}".format(post['id'], post['text'].encode('utf8')))

                r = api.request('statuses/show/:%d' % post['id']).json()
                if 'errors' in r:
                    logger.error("We got an error message: {0} Code: {1}".format(r['errors'][0]['message'],
                                                                                 r['errors'][0]['code']))
                    post_list.pop(0)
                else:
                    user_item = r['user']
                    user_id = user_item['id']

                    if not user_id in ignore_list:

                        r = api.request('statuses/retweet/:{0}'.format(post['id']))
                        CheckError(r)
                        post_list.pop(0)

                        if not 'errors' in r.json():

                        	CheckForFollowRequest(post)
                        	CheckForFavoriteRequest(post)

                    else:
                        post_list.pop(0)
                        logger.info("Blocked user's tweet skipped")
            else:
                post_list.pop(0)
                logger.error("We got an error message: {0} Code: {1}".format(post['errors'][0]['message'],
                                                                             post['errors'][0]['code']))
        else:
            logger.info("Ratelimit at {0}% -> pausing retweets".format(ratelimit[2]))


# Check if a post requires you to follow the user.
# Be careful with this function! Twitter may write ban your application
# for following too aggressively
def CheckForFollowRequest(item):
    text = item['text']
    if any(x in text.lower() for x in follow_keywords):
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

# FIFO - Every new follow should result in the oldest follow being removed.


def RemoveOldestFollow():
    friends = list()
    for id in api.request('friends/ids'):
        friends.append(id)

    oldest_friend = friends[-1]

    if len(friends) > max_follows:

        r = api.request('friendships/destroy', {'user_id': oldest_friend})

        if r.status_code == 200:
            status = r.json()
            logger.info('Unfollowed: {0}'.format(status['screen_name']))

    else:
        logger.info("No friends unfollowed")

    del friends[:]
    del oldest_friend

# Check if a post requires you to favorite the tweet.
# Be careful with this function! Twitter may write ban your application
# for favoriting too aggressively


def CheckForFavoriteRequest(item):
    text = item['text']

    if any(x in text.lower() for x in fav_keywords):
        try:
            r = api.request('favorites/create', {'id': item['retweeted_status']['id']})
            CheckError(r)
            logger.info("Favorite: {0}".format(item['retweeted_status']['id']))
        except:
            r = api.request('favorites/create', {'id': item['id']})
            CheckError(r)
            logger.info("Favorite: {0}".format(item['id']))

# Clear the post list queue in order to avoid a buildup of old posts


def ClearQueue():
    post_list_length = len(post_list)

    if post_list_length > min_posts_queue:
        del post_list[:post_list_length - min_posts_queue]
        logger.info("===THE QUEUE HAS BEEN CLEARED===")

# Check list of blocked users and add to ignore list


def CheckBlockedUsers():

    if not ratelimit_search[2] < min_ratelimit_search:

        for b in api.request('blocks/ids'):
            if not b in ignore_list:
                ignore_list.append(b)
                logger.info("Blocked user {0} added to ignore list".format(b))
    else:

        logger.warn("Update blocked users skipped! Queue: {0} Ratelimit: {1}/{2} ({3}%)".format(len(post_list),
                                                                                                ratelimit_search[1],
                                                                                                ratelimit_search[0],
                                                                                                ratelimit_search[2]))

# Scan for new contests, but not too often because of the rate limit.


def ScanForContests():

    global ratelimit_search

    if not ratelimit_search[2] < min_ratelimit_search:

        logger.info("=== SCANNING FOR NEW CONTESTS ===")

        for search_query in search_queries:

            logger.info("Getting new results for: {0}".format(search_query))

            try:
                r = api.request( 'search/tweets', {'q': search_query, 'result_type': "mixed", 'count': 50})
                CheckError(r)
                c = 0

                for item in r:

                    c = c + 1
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

                        if not original_id in ignore_list:

                            if not original_user_item['id'] in ignore_list:

                                post_list.append(original_item)

                                logger.info("{0} - {1} retweeting {2} - {3} : {4}".format(id, screen_name, original_id,
                                                                                          original_screen_name,text))

                                ignore_list.append(original_id)

                            else:

                                logger.info("{0} ignored {1} clocked and in ignore list".format(id,
                                                                                                original_screen_name))
                        else:

                            logger.debug("{0} ignored {1} in ignore list".format(id, original_id))

                    else:

                        if not id in ignore_list:

                            if not user_item['id'] in ignore_list:

                                post_list.append(item)

                                logger.debug("{0} - {1} : {2}".format(id, screen_name, text))
                                ignore_list.append(id)

                            else:

                                logger.info("{0} ignored {1} blocked user in ignore list".format(id, screen_name))
                        else:

                            logger.debug("{0} in ignore list".format(id))

                logger.info("Got {0} results".format(c))

            except Exception as e:
                logger.exception("Could not connect to TwitterAPI - are your credentials correct?")

    else:

        logger.warn("Search skipped! Queue: {0} Ratelimit: {1}/{2} ({3}%)".format(len(post_list),
                                                                                  ratelimit_search[1],
                                                                                  ratelimit_search[0],
                                                                                  ratelimit_search[2]))


class PeriodicScheduler(sched.scheduler):

    def __init__(self, timefunc=time.time, delayfunc=time.sleep):
        # List of tasks tha will be periodically be called
        # tasks are stored as tuples: (delay, priority, action)
        self.tasks = []
        super().__init__(timefunc, delayfunc)

    def enter(self, delay, priority, action):
        self.tasks.append((delay, priority, action))

    def run(self, blocking=True):
        for i in range(len(self.tasks)):
            self.run_task(i)

        super().run(blocking)

    def enter_task(self, index):
        super().enter(self.tasks[index][0], self.tasks[index][1], self.run_task, argument=(index,))

    def run_task(self, index):
        self.enter_task(index)
        t = threading.Thread(target=self.tasks[index][2])
        t.daemon = True
        try:
            t.run()
        except Exception:
            logger.exception("Exception in thread")


s = PeriodicScheduler()

s.enter(clear_queue_time, 1, ClearQueue)
s.enter(rate_limit_update_time, 2, CheckRateLimit)
s.enter(blocked_users_update_time, 3, CheckBlockedUsers)
s.enter(scan_update_time, 4, ScanForContests)
s.enter(retweet_update_time, 5, UpdateQueue)

s.run()
