from TwitterAPI import TwitterAPI


class TwitterClient():

    def __init__(self, consumer_key, consumer_secret, access_token_key, access_token_secret):
        self.api = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret)
        self.ratelimits = None

    def search_tweets(self, query, limit, result_type='mixed'):
        r = self._api_call('search/tweets', {'q': query, 'result_type': result_type, 'count': limit})
        return r['statuses']

    def get_tweet(self, post_id):
        return self._api_call('statuses/show/:{}'.format(post_id))

    def retweet(self, post_id):
        return self._api_call('statuses/retweet/:{}'.format(post_id))

    def get_friends_ids(self):
        return self._api_call('friends/ids')['ids']

    def follow(self, username):
        return self._api_call('friendships/create', {'screen_name': username})

    def unfollow(self, user_id):
        return self._api_call('friendships/destroy', {'user_id': user_id})

    def favorite(self, post_id):
        return self._api_call('favorites/create', {'id': post_id})

    def get_blocks(self):
        return self._api_call('blocks/ids')['ids']

    def update_ratelimits(self):
        r = self._api_call('application/rate_limit_status')['resources']

        #flatten dictionary
        self.ratelimits = dict()
        for x in r.values():
            self.ratelimits.update(x)

        #create percent
        for x in self.ratelimits.values():
            x['percent'] = x['remaining']/x['limit'] * 100

    def _api_call(self, request, parameters=None):
        r = self.api.request(request, parameters)
        return r.json()