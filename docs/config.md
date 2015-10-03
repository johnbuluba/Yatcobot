# Config options

The config file written in json. If some values are not in the config
_reasonable_  hardcoded defaults are used

Example config with default values:
```
{
    "consumer_key": "",
    "consumer_secret": "",
    "access_token_key": "",
    "access_token_secret": "",
    "search_queries": ["RT to win", "Retweet and win"],
    "follow_keywords": ["follow", "follower"],
    "fav_keywords": ["fav", "favorite"],
    "priority_keywords": ["ps4", "iphone"],
    "retweet_interval": 600,
    "retweet_random_margin": 60,
    "scan_interval": 5400,
    "max_queue": 60,
    "clear_queue_interval":43200,
    "rate_limit_update_interval":60,
    "min_ratelimit_percent":10,
    "blocked_users_update_interval": 300,
    "max_follows": 1950
}
```
---
- #### consumer_key, consumer_secret, access_token_key, access_token_secret:
The twitter api keys that are needed for interacti with the twitter api.
Obtain them from [here](https://apps.twitter.com/)

- #### search_queries 
This are the queries that are used to find contests from the twitter. It works
like the twitter search bar, so you can experiment there first

- #### follow_keywords
This keywords are searched inside the tweet's text to determinate if it is
needed to follow the original poster.

- #### fav_keywords
This keywords are searched inside the tweet's text to determinate if it is
needed to favorite the original post.

- #### priority_keywords
This keywords are used to promote contests that contain this keywords so the
bot enters more contests that the user is interested in

- #### retweet_interval
How often a retweet will be posted. (_seconds_)

- #### retweet_random_margin
Adds randomness to the post interval. For example if retweet_interval is 600
and retweet_random_margin is 60 retweets will be posted every 9-11 minutes.
 (_seconds_)

- ####  scan_interval
How often will search for new tweets from twitter. (_seconds_)

- #### max_queue
The maximum number of tweets that are in the queue to be retweeted.
If queue is bigger, some will be deleted. (_seconds_)

- #### clear_queue_interval
How often the queue will be checked so if the number is over max_queue, delete
some posts. (_seconds_)

- #### min_ratelimit_percent
Twitter api has a limit on how many api calls you can make on a period of time.
The bot checks the remaining api calls and if its bellow min_ratelimit_percent
it pauses.

- #### blocked_users_update_interval
The interval to update the twitter blocked users so you dont retweet posts
from unwanted users. (_seconds_)

- #### max_follows
The maximum follows the user has. If user follows exceeds max_follows the oldests
follow will be unfollowed.
