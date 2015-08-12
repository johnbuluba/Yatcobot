from TwitterAPI import TwitterAPI
import threading
import time

consumer_key = "YOUR CONSUMER KEY"
consumer_secret = "YOUR CONSUMER SECRET"
access_token_key = "YOUR ACCESS TOKEN KEY"
access_token_secret = "YOUR ACCESS TOKEN SECRET"

api = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret)

post_list = list()

last_twitter_id = 0

def UpdateQueue():
    u = threading.Timer(5.0, UpdateQueue)
    u.daemon = True;
    u.start()

    print("=== CHECKING RETWEET QUEUE ===")

    if len(post_list) > 0:
        post = post_list[0]
        print("Retweeting: " + str(post))

        api.request('statuses/retweet/:' + str(post))
        post_list.pop(0)


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

            post_list.append(item['id'])

            print(item)


ScanForContests()
UpdateQueue()

while (True):
    time.sleep(1)
