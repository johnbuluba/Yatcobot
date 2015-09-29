import time
import datetime
import logging

from TwitterAPI import TwitterAPI

from .config import Config


logger = logging.getLogger(__name__)


class TwitterClientException(Exception):
    pass


class TwitterClientRetweetedException(Exception):
    pass


class TwitterClient():

    def __init__(self, consumer_key, consumer_secret, access_token_key, access_token_secret):
        self.api = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret)
        self.ratelimits = dict()

    def search_tweets(self, query, limit, result_type='mixed'):
        self._check_ratelimit('/search/tweets')
        r = self._api_call('search/tweets', {'q': query, 'result_type': result_type, 'count': limit})
        return r['statuses']

    def get_tweet(self, post_id):
        self._check_ratelimit('/statuses/show/:id')
        return self._api_call('statuses/show/:{}'.format(post_id))

    def retweet(self, post_id):
        return self._api_call('statuses/retweet/:{}'.format(post_id))

    def get_friends_ids(self):
        self._check_ratelimit('/friends/ids')
        return self._api_call('friends/ids')['ids']

    def follow(self, username):
        return self._api_call('friendships/create', {'screen_name': username})

    def unfollow(self, user_id):
        return self._api_call('friendships/destroy', {'user_id': user_id})

    def favorite(self, post_id):
        return self._api_call('favorites/create', {'id': post_id})

    def get_blocks(self):
        self._check_ratelimit('/blocks/ids')
        return self._api_call('blocks/ids')['ids']

    def update_ratelimits(self, check_ratelimit=True):

        # if ratelimit dictionary empty dont check for rates
        if check_ratelimit:
            self._check_ratelimit('/application/rate_limit_status')

        #ratelimit_check controls if before the api_call we check the ratelimit. Usefull to be false the first update
        r = self._api_call('application/rate_limit_status')['resources']

        #flatten dictionary
        self.ratelimits = dict()
        for x in r.values():
            self.ratelimits.update(x)
        #create percent
        for x in self.ratelimits.values():
            x['percent'] = x['remaining']/x['limit'] * 100

        #log ratelimit status
        logger.debug("Ratelimit status: {}".format({key: item['percent'] for key, item in self.ratelimits.items()
                                                                         if item['percent'] < 100}))

    def _api_call(self, request, parameters=None):
        r = self.api.request(request, parameters)
        response_dict = r.json()
        #check for errors
        if 'errors' in response_dict:
            for error in response_dict['errors']:
                message = error['message']
                code = error['code']
                if message == 'You have already retweeted this tweet.':
                    raise TwitterClientRetweetedException()

                logger.error('Error during twitter api call {} (parameters: {}): {}'.format(request, parameters, message))

            raise TwitterClientException('Error during twitter api call {}'.format(request))

        return response_dict

    def _check_ratelimit(self, request):

        #Check if ratelimits is empty. Id its empty, call update_ratelimits
        if len(self.ratelimits) == 0:
            self.update_ratelimits(False)

        resource_ratelimit = self.ratelimits[request]

        # if over threshold sleep untill reset
        if resource_ratelimit['percent'] < Config.min_ratelimit_percent:

            reset_time = resource_ratelimit['reset']
            now = int(datetime.datetime.now().strftime('%s'))
            wait = reset_time - now

            if wait > 0:
                logger.warning('Rate limit {}. Waiting for {} seconds'.format(resource_ratelimit['percent'], wait))
                time.sleep(wait)
                #Update ratelimits again
                self.update_ratelimits(check_ratelimit=False)



