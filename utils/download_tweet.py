import argparse
import json
from yatcobot.client import TwitterClient
from yatcobot.config import Config

parser = argparse.ArgumentParser(description='Download a tweet to json')
parser.add_argument('tweet_id', metavar='id', type=int)
parser.add_argument('--config', '-c', dest='config', default='../config.json', help='Path of the config file')

args = parser.parse_args()

Config.load(args.config)

client = TwitterClient(Config.consumer_key,
                       Config.consumer_secret,
                       Config.access_token_key,
                       Config.access_token_secret)

tweet = client.get_tweet(args.tweet_id)

with open('{}.json'.format(args.tweet_id), 'w') as f:
    json.dump(tweet, f, indent=2)

