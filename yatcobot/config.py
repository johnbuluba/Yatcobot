import json


class Config:
    """Class that contains all  config variables. It loads user values from a json file """

    # Default values
    consumer_key = None
    consumer_secret = None
    access_token_key = None
    access_token_secret = None
    retweet_interval = 600
    retweet_random_margin = 60
    scan_interval = 5400
    clear_queue_interval = 43200
    max_queue = 60
    rate_limit_update_interval = 60
    min_ratelimit_percent = 10
    blocked_users_update_interval = 300
    max_follows = 1950
    search_queries = ["RT to win", "Retweet and win"]
    follow_keywords = [" follow ", " follower "]
    fav_keywords = [" fav ", " favorite "]
    priority_keywords = ["ps4", "pc"]

    @staticmethod
    def load(filename):
        # Load our configuration from the JSON file.
        with open(filename) as data_file:
            data = json.load(data_file)

        for key, value in data.items():
            setattr(Config, key, value)

    @staticmethod
    def save_user_tokens(filename, token, secret):
        with open(filename) as data_file:
            data = json.load(data_file)

        data['access_token_key'] = token
        data['access_token_secret'] = secret

        with open(filename, 'w') as data_file:
            json.dump(data, data_file, indent=4)