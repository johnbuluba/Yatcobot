import json


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
    min_ratelimit_percent = 10
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
            setattr(Config, key, value)