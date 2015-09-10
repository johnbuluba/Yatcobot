from TwitterAPI import TwitterAPI
import threading
import time
import json
import os.path

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
search_queries = data["search-queries"]
follow_keywords = data["follow-keywords"]
fav_keywords = data["fav-keywords"]

# Don't edit these unless you know what you're doing.
api = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret)
post_list = list()
ignore_list = list()
#last_twitter_id = 0

if os.path.isfile('ignorelist'):
	print("Loading ignore list")
	with open('ignorelist') as f:
		ignore_list = f.read().splitlines()
	f.close()
	print ignore_list
	time.sleep(1)


# Print and log the text
def LogAndPrint( text ):
	tmp = text.replace("\n","")
	print(tmp)
	f_log = open('log', 'a')
	f_log.write(tmp + "\n")
	f_log.close()


# Update the Retweet queue (this prevents too many retweets happening at once.)
def UpdateQueue():
	u = threading.Timer(retweet_update_time, UpdateQueue)
	u.daemon = True;
	u.start()

	print("=== CHECKING RETWEET QUEUE ===")

	print("Queue length: " + str(len(post_list)))

	if len(post_list) > 0:
		post = post_list[0]
		LogAndPrint("Retweeting: " + str(post['id']) + " " + str(post['text'].encode('utf8')))

		CheckForFollowRequest(post)
		CheckForFavoriteRequest(post)

		api.request('statuses/retweet/:' + str(post['id']))
		post_list.pop(0)


# Check if a post requires you to follow the user.
# Be careful with this function! Twitter may write ban your application for following too aggressively
def CheckForFollowRequest(item):
	text = item['text']
	if any(x in text.lower() for x in follow_keywords):
		try:
			api.request('friendships/create', {'screen_name': item['retweeted_status']['user']['screen_name']})
			LogAndPrint("Follow: " + item['retweeted_status']['user']['screen_name'])
		except:
			user = item['user']
			screen_name = user['screen_name']
			api.request('friendships/create', {'screen_name': screen_name})
			LogAndPrint("Follow: " + screen_name)


# Check if a post requires you to favorite the tweet.
# Be careful with this function! Twitter may write ban your application for favoriting too aggressively
def CheckForFavoriteRequest(item):
	text = item['text']
	if any(x in text.lower() for x in fav_keywords):
		try:
			api.request('favorites/create', {'id': item['retweeted_status']['user']['id']})
			LogAndPrint("Favorite: " + item['retweeted_status']['user']['id'])
		except:
			api.request('favorites/create', {'id': item['id']})
			LogAndPrint("Favorite: " + item['id'])


# Scan for new contests, but not too often because of the rate limit.
def ScanForContests():
	t = threading.Timer(scan_update_time, ScanForContests)
	t.daemon = True;
	t.start()

#	global last_twitter_id
	
	print("=== SCANNING FOR NEW CONTESTS ===")


	for search_query in search_queries:

		print("Getting new results for: " + search_query)
	
		try:
#			r = api.request('search/tweets', {'q':search_query, 'since_id':last_twitter_id})
			r = api.request('search/tweets', {'q':search_query, 'result_type':"mixed", 'count':100})
			c=0
				
			for item in r:
				
				c=c+1
				user_item = item['user']
				screen_name = user_item['screen_name']
				text = item['text']
				text = text.replace("\n","")
				id = str(item['id'])
				original_id=id
				is_retweet = 0

#				if (item['id'] > last_twitter_id):
#					last_twitter_id = item['id']

				if 'retweeted_status' in item:

					is_retweet = 1
					original_item = item['retweeted_status']
					original_id = str(original_item['id'])
					original_user_item = original_item['user']
					original_screen_name = original_user_item['screen_name']

					if not original_id in ignore_list:

						if not original_screen_name in ignore_list:
				
							if item['retweet_count'] > 0:

								post_list.append(item)
								f_ign = open('ignorelist', 'a')

								if is_retweet:
									print(id + " - " + screen_name + " retweeting " + original_id + " - " + original_screen_name + ": " + text)
									ignore_list.append(original_id)
									f_ign.write(original_id + "\n")
								else:
									print(id + " - " + screen_name + ": " + text)
									ignore_list.append(id)
									f_ign.write(id + "\n")

								f_ign.close()

						else:
		
							if is_retweet:
								print(id + " ignored: " + original_screen_name + " on ignore list")
							else:
								print(original_screen_name + " in ignore list")

					else:

						if is_retweet:
							print(id + " ignored: " + original_id + " on ignore list")
						else:
							print(id + " in ignore list")

				if not id in ignore_list:

					if not screen_name in ignore_list:
				
						if item['retweet_count'] > 0:

							post_list.append(item)
							f_ign = open('ignorelist', 'a')

							if is_retweet:
								print(id + " - " + screen_name + " retweeting " + original_id + " - " + original_screen_name + ": " + text)
								ignore_list.append(original_id)
								f_ign.write(original_id + "\n")
							else:
								print(id + " - " + screen_name + ": " + text)
								ignore_list.append(id)
								f_ign.write(id + "\n")

							f_ign.close()

					else:
		
						if is_retweet:
							print(id + " ignored: " + original_screen_name + " on ignore list")
						else:
							print(original_screen_name + " in ignore list")

				else:

					if is_retweet:
						print(id + " ignored: " + original_id + " on ignore list")
					else:
						print(id + " in ignore list")
			
			print("Got " + str(c) + " results")
#			print("Last ID: " + str(last_twitter_id))

		except Exception as e:
			print("Could not connect to TwitterAPI - are your credentials correct?")
			print("Exception: " + e)


ScanForContests()
UpdateQueue()

while (True):
    time.sleep(1)
