from TwitterAPI import TwitterAPI
import threading
import time
import json

# Load our configuration from the JSON file.
with open('config.json') as data_file:    
    data = json.load(data_file)

# These vars are loaded in from config.
consumer_key = data["consumer-key"]
consumer_secret = data["consumer-secret"]
access_token_key = data["access-token-key"]
access_token_secret = data["access-token-secret"]
retweet_update_time = data["retweet-update-time"]

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
    	try:
    	    api.request('friendships/create', {'screen_name': item['retweeted_status']['user']['screen_name']
    	except:
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
	
	try:
		r = api.request('search/tweets', {'q':'RT to win', 'since_id':last_twitter_id})

		for item in r:
			if item['retweet_count'] > 0:
				if (item['id'] > last_twitter_id):
					last_twitter_id = item['id']

				post_list.append(item)
				print(item)
	except Exception as e:
		print("Could not connect to TwitterAPI - are your credentials correct?")


ScanForContests()
UpdateQueue()

while (True):
    time.sleep(1)
