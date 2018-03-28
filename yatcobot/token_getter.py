import logging
import webbrowser

from requests_oauthlib import OAuth1Session

REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
SIGNIN_URL = 'https://api.twitter.com/oauth/authenticate'

logger = logging.getLogger(__name__)


def get_access_token(consumer_key, consumer_secret):
    """
    Gets the user tokens from  twitter given application tokens
    :param consumer_key: Consumer api key
    :param consumer_secret: Consumer secret api key
    :return: dict {'token': token, 'secret': secret}
    """
    oauth_client = OAuth1Session(consumer_key, client_secret=consumer_secret)

    logger.info('Requesting temp token from Twitter')

    try:
        resp = oauth_client.fetch_request_token(REQUEST_TOKEN_URL)
    except ValueError as e:
        logger.error('Invalid respond from Twitter requesting temp token: %s' % e)
        raise

    url = oauth_client.authorization_url(AUTHORIZATION_URL)

    logger.info('I will try to start a browser to visit the following Twitter page')
    logger.info('if a browser will not start, copy the URL to your browser')
    logger.info('and retrieve the pincode to be used')
    logger.info('the next step to obtaining an Authentication Token:')

    logger.info(url)

    webbrowser.open(url)
    pincode = input('Pincode? ')

    logger.info('Generating and signing request for an access token')

    oauth_client = OAuth1Session(consumer_key, client_secret=consumer_secret,
                                 resource_owner_key=resp.get('oauth_token'),
                                 resource_owner_secret=resp.get('oauth_token_secret'),
                                 verifier=pincode
                                 )
    try:
        resp = oauth_client.fetch_access_token(ACCESS_TOKEN_URL)
    except ValueError as e:
        logger.error('Invalid respond from Twitter requesting access token: %s' % e)
        raise

    token = resp.get('oauth_token')
    secret = resp.get('oauth_token_secret')
    logger.info('Your Twitter Access Token key: %s' % token)
    logger.info('Access Token secret: %s' % secret)

    return {'token': token, 'secret': secret}
