import time
import datetime
import logging
import re

from TwitterAPI import TwitterAPI, constants

from .config import Config


logger = logging.getLogger(__name__)


class TwitterClientException(Exception):
    pass


class TwitterClientRetweetedException(Exception):
    pass


class RateLimiterExpired(Exception):
    pass


class RateLimiter(dict):

    def refresh_limits(self, new_limits):

        #delete old values
        self.clear()

        #flatten dictionay
        for value in new_limits.values():
            for key, limits in value.items():
                #replace parameters in url like :id :slug to :PARAM
                key = re.sub(r'\/:[a-z_]+', '/:PARAM', key)
                self[key] = limits

        #create percent
        for key in self.keys():
            self._calculate_percent_remaining(key)

    def check_limit(self, endpoint):

        #Only GET methods have ratelimits
        if constants.ENDPOINTS[endpoint][0] == 'POST':
            return

        logger.debug('Checking limits for {}'.format(endpoint))

        endpoint_limits = self[self._get_internal_endpoint_name(endpoint)]

        # if over threshold sleep untill reset
        if endpoint_limits['percent'] < Config.min_ratelimit_percent:

            reset_time = endpoint_limits['reset']
            now = int(datetime.datetime.now().strftime('%s'))
            wait = reset_time - now

            if wait > 0:
                logger.warning('Rate limit {}. Waiting for {} seconds'.format(endpoint_limits['percent'], wait))
                time.sleep(wait)
                raise RateLimiterExpired()

    def decrease_remaining(self, endpoint):
        endpoint = self._get_internal_endpoint_name(endpoint)
        if endpoint in self:
            self[endpoint]['remaining'] -= 1
            logger.debug('Decreased remainin usages of {}. New value {}'. format(endpoint, self[endpoint]['remaining']))
            self._calculate_percent_remaining(endpoint)

    def _calculate_percent_remaining(self, endpoint):
        self[endpoint]['percent'] = self[endpoint]['remaining']/self[endpoint]['limit'] * 100

    def _get_internal_endpoint_name(self, endpoint):
        return '/' + endpoint


class TwitterClient:

    def __init__(self, consumer_key, consumer_secret, access_token_key, access_token_secret):
        self.api = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret)
        self.ratelimiter = RateLimiter()
        self.update_ratelimits(check_ratelimit=False)

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

    def update_ratelimits(self, check_ratelimit=True):

        #ratelimit_check controls if before the api_call we check the ratelimit. Usefull to be false the first update
        r = self._api_call('application/rate_limit_status',check_ratelimit=check_ratelimit)['resources']

        self.ratelimiter.refresh_limits(r)

        #log ratelimit status
        logger.debug("Ratelimit status: {}".format({key: item['percent'] for key, item in self.ratelimiter.items()
                                                                         if item['percent'] < 100}))

    def _api_call(self, request, parameters=None, check_ratelimit=True):

        _, endpoint = self.api._get_endpoint(request)

        if check_ratelimit:


            try:
                self.ratelimiter.check_limit(endpoint)
            except RateLimiterExpired:
                self.update_ratelimits(check_ratelimit=False)

        r = self.api.request(request, parameters)

        self.ratelimiter.decrease_remaining(endpoint)

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




