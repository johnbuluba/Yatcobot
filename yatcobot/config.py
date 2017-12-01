import json


class Config:
    """Class that contains all  config variables. It loads user values from a json file """

    # Default values
    consumer_key = None
    consumer_secret = None
    access_token_key = None
    access_token_secret = None
    pushbullet_token = None
    retweet_interval = 600
    retweet_random_margin = 60
    scan_interval = 5400
    clear_queue_interval = 43200
    max_queue = 60
    rate_limit_update_interval = 60
    min_ratelimit_percent = 10
    blocked_users_update_interval = 300
    max_follows = 1950
    min_quote_similarity = 0.50
    max_quote_depth = 10
    check_mentions_interval = 600
    search_queries = ["RT to win", "Retweet and win"]
    follow_keywords = ["follow", "follower"]
    fav_keywords = ["fav", "favorite"]
    priority_keywords = ["ps4", "pc"]
    search_language = None

    @staticmethod
    def load(filename):
        """
        Loads a file and imports the settings
        :param filename: the file to import
        """
        # Load our configuration from the JSON file.
        with open(filename) as data_file:
            data = json.load(data_file)

        for key, value in data.items():
            if value == "":
                value = None
            setattr(Config, key, value)
        b = Config.search_language
        a = 5

    @staticmethod
    def save_user_tokens(filename, token, secret):
        """
        Saves the user tokens to the config file
        :param filename: the destination config file
        :param token: the user token
        :param secret: the user token secret
        """
        with open(filename) as data_file:
            data = json.load(data_file)

        data['access_token_key'] = token
        data['access_token_secret'] = secret

        with open(filename, 'w') as data_file:
            json.dump(data, data_file, indent=4)