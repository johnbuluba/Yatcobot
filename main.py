from TwitterAPI import TwitterAPI
import threading
import time

# Fill these in with your Twitter API auth details.
consumer_key = "YOUR CONSUMER KEY"
consumer_secret = "YOUR CONSUMER SECRET"
access_token_key = "YOUR ACCESS TOKEN KEY"
access_token_secret = "YOUR ACCESS TOKEN SECRET"

# How many seconds have to pass for 1 retweet/follow to be made?
# The higher the number, the less retweets will be made in a day.
retweet_update_time = 5.0

# Don't edit these unless you know what you're doing.
api = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret)
post_list = list()
last_twitter_id = 0

# Update the Retweet queue (this prevents too many retweets happening at once.)
def UpdateQueue():
    u = threading.Timer(retweet_update_time, UpdateQueue)
    u.daemon = True;
    u.start()

    print("=== CHECKING RETWEET QUEUE ===")

    if len(post_list) > 0:
        post = post_list[0]
        print("Retweeting: " + str(post['id']))
        
        CheckForFollowRequest(post)
        
        api.request('statuses/retweet/:' + str(post['id']))
        post_list.pop(0)


# Check if a post requires you to follow the user.
def CheckForFollowRequest(item):
    text = item['text']
    if "follow" in text.lower():
        user = item['user']
        screen_name = user['screen_name']
        api.request('friendships/create', {'screen_name': screen_name})


# Scan for new contests, but not too often because of the rate limit.
def ScanForContests():
    t = threading.Timer(10.0, ScanForContests)
    t.daemon = True;
    t.start()

    global last_twitter_id

    print("=== SCANNING FOR NEW CONTESTS ===")

    r = api.request('search/tweets', {'q':'RT to win', 'since_id':last_twitter_id})

    for item in r:
        if item['retweet_count'] > 0:
            if (item['id'] > last_twitter_id):
                last_twitter_id = item['id']

            post_list.append(item)
            print(item)


ScanForContests()
UpdateQueue()

while (True):
    time.sleep(1)
