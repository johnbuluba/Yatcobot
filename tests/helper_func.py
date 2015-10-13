import random
import string


def get_random_string(length=10):
    return''.join([random.choice(string.ascii_letters + string.digits) for n in range(length)])

def create_post(id=None, userid=None, retweets=None, favorites=None, user_followers=None, text=None, date=None):
    id = random.randint(0, 10000000) if id is None else id
    userid = random.randint(0, 10000000) if userid is None else userid
    retweets = random.randint(0, 1000) if retweets is None else retweets
    favorites = random.randint(0, 1000) if favorites is None else favorites
    user_followers = random.randint(0, 1000) if user_followers is None else user_followers
    text = "test" if text is None else text
    date = 'Thu Oct 08 08:34:51 +0000 2015' if date is None else date

    user = {'followers_count': user_followers,
             'id': userid,
             'screen_name': get_random_string()
    }

    return {'id': id, 'retweet_count': retweets, 'favorite_count': favorites, 'text': text,
             'created_at': date, 'user': user}