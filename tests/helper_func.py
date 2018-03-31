import json
import random
import string
import os

from yatcobot.config import Config


tests_path = path = os.path.dirname(os.path.abspath(__file__))


def get_random_string(length=10):
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(length)])


def create_post(id=None, userid=None, retweets=None, favorites=None, user_followers=None,
                full_text=None, date=None):
    id = random.randint(0, 10000000) if id is None else id
    userid = random.randint(0, 10000000) if userid is None else userid
    retweets = random.randint(0, 1000) if retweets is None else retweets
    favorites = random.randint(0, 1000) if favorites is None else favorites
    user_followers = random.randint(0, 1000) if user_followers is None else user_followers
    text = "test" if full_text is None else full_text
    date = 'Thu Oct 08 08:34:51 +0000 2015' if date is None else date

    user = {'followers_count': user_followers,
            'id': userid,
            'screen_name': get_random_string()
            }

    return {'id': id, 'retweet_count': retweets, 'favorite_count': favorites, 'full_text': text,
            'created_at': date, 'user': user}


def get_fixture(filename, raw=False):
    with open(tests_path + '/fixtures/' + filename) as f:
        response = f.read()
    if raw:
        return response

    return json.loads(response)


def load_fixture_config():
    tests_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(tests_path, 'fixtures', 'config.test.yaml')
    Config.load(config_path)
