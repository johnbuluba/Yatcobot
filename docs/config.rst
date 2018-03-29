==============
Config options
==============

The config file written in yaml. If some values are not in the config
*reasonable* hardcoded defaults are used

Example config with default values:

.. code-block:: yaml

    # Client settings
    
    # consumer key for twitter api
    consumer_key: null
    # consumer secret for twitter api
    consumer_secret: null
    # access token key for twitter api
    access_token_key: null
    # access token secret for twitter api
    access_token_secret: null
    
    # The bot will stop when api calls remaining are under
    # min_ratelimit_percent of the max that twitter allows
    min_ratelimit_percent: 10
    
    
    # Search for contest settings
    search:
    
      # Queries to use for searching giveaways.
      # You can set the language for a specific query like this
      # - query
      # - query with language filter:
      #   lang: en
      queries:
        - RT to win
        - Retweet and win
        - Giveaway retweet
    
      # Max tweets that holds the bot in memory to post
      max_queue: 100
    
      # The maximum quotes that will be recursively search
      # for the original tweet
      max_quote_depth: 20
      # Some tweets are quotes of another tweet
      # This is the mimimum similary between the quote and the post
      min_quote_similarity: 0.5
      # Keywords that if they appear in a post it will get
      # priority for retweet
      priority_keywords: ["pc", "iphone"]
    
    # Actions that some giveaways require to enter
    actions:
      # Follow the user that posts the giveaway
      follow:
        # If this action is enabled
        enabled: true
        # Keywords to search in post for follow action
        keywords: ["follow", "follower"]
        # When max_following is reached, will unfollow oldest follows
        max_following: 1950
      # Favorite the post
      favorite:
        # If this action is enabled
        enabled: true
        # Keywords to search in post for favorite action
        keywords: ["fav", "favorite"]
    
    # Intervals of bot tasks
    scheduler:
      # How often will search for new posts
      search_interval: 5400
      # How often will retweet
      retweet_interval: 600
      # A random margin from retweet interval to avoid bot detection
      retweet_random_margin: 60
      # Update blocked users list so posts of them are not retweeted
      blocked_users_update_interval: 300
      # How often will delete oldest posts in queue
      clear_queue_interval: 60
      # How often will update the remaining api rate limits
      rate_limit_update_interval: 60
      # How often will check for new mentions
      check_mentions_interval: 600
    
    # Notifiers will notify when somenone mentions the user.(Possible win)
    notifiers:
      # Pushbullet notifier
      pushbullet:
        # If the notifier is enabled
        enabled: false
        # Pushbullet api token
        token: my_pushbullet_token
    


Global
======

consumer_key, consumer_secret, access_token_key, access_token_secret
--------------------------------------------------------------------

The twitter api keys that are needed for interacting with the twitter
api. Obtain them from `here <https://apps.twitter.com/>`__


Search
======
Here are defined all the search related settings


queries
-------

These are the queries that are used to find contests from the
twitter. It works like the twitter search bar, so you can experiment
there first

Queries are defined as a sequence. It can be strings or mapppings with additional option

For example

.. code-block:: yaml

    search:
        queries:
          - RT to win
          - retweet giveaway
          # You can set a language option for a query
          - Διαγωνισμός:
            lang: el


max_queue
---------

The maximum number of tweets that are in the queue to be retweeted.
If queue is bigger, some will be deleted. (*seconds*)


max_quote_depth
---------

Some posts are quotes that quoting other quote(..that quoting other
quote). So we need to follow the quotes to find the original post
that is the contest. This value defines the max quotes that we will
follow to get the original post


min_quote_similarity
--------------------

When the bot gets new tweets, it checks if they are a quote of a
contest (some people quote the contest, they dont retweet them). To
get rid of that, the similarity between the quote and the post is
compared. This is the threshold which we get the quoted tweet as the
contest and not the one we got. 1.0 means 100% the same


priority_keywords
-----------------

These keywords are used to promote contests that contain this
keywords so the bot enters more contests that the user is interested
in



Actions
=======
Here are defined all the action settings. Actions are requests
that contests have, like follow and fovorite


follow
------

enabled
^^^^^^^
If the follow action is enabled

keywords
^^^^^^^^
These keywords are searched inside the tweet's text to determinate if
it is needed to follow the original poster.


favorite
--------

enabled
^^^^^^^
If the favorite action is enabled

keywords
^^^^^^^^
These keywords are searched inside the tweet's text to determinate if
it is needed to favorite the original post.


Schduler
========

Intervals of bot tasks

search_interval
--------------
How often will search for new tweets from twitter. (*seconds*)

retweet_interval
----------------
How often a retweet will be posted. (*seconds*)

retweet_random_margin
---------------------
Adds randomness to the post interval. For example if
retweet\_interval is 600 and retweet\_random\_margin is 60, retweets
will be posted every 9-11 minutes. (*seconds*)


blocked_users_update_interval
-----------------------------
The interval to update the twitter blocked users so you dont retweet
posts from unwanted users. (*seconds*)

clear_queue_interval
--------------------
How often the queue will be checked so if the number is over
max\_queue, delete some posts. (*seconds*)

rate_limit_update_interval
--------------------------
How often will update for the remaining api calls


check_mentions_interval
-----------------------

How often we check if the user is mentioned in a tweet. We check this
because many contests mention the winners in a tweet, so we can
notify the user for a possible win.


   





-  .. rubric:: max\_queue
      :name: max_queue

   The maximum number of tweets that are in the queue to be retweeted.
   If queue is bigger, some will be deleted. (*seconds*)




-  .. rubric:: min\_ratelimit\_percent
      :name: min_ratelimit_percent

   Twitter api has a limit on how many api calls you can make on a
   period of time. The bot checks the remaining api calls and if it's
   bellow min\_ratelimit\_percent it pauses.








-  .. rubric:: max\_follows
      :name: max_follows

   The maximum follows the user has. If user follows exceeds
   max\_follows the oldest follow will be unfollowed.

-  .. rubric:: check\_mentions\_interval
      :name: check_mentions_interval


-  .. rubric:: pushbullet\_token
      :name: pushbullet_token

   Its the api token of pushbullet. It is used to notify you when
   someone is mentioned you in a tweet.
