#!/usr/bin/env python3
import argparse
from yatcobot.bot import Yatcobot
from yatcobot.token_getter import get_access_token
from yatcobot.config import Config

config_file = 'config.json'
Config.load(config_file)


parser = argparse.ArgumentParser(description='Yatcobot: a bot for entering twitter contests')
parser.add_argument('--login', dest='login', action='store_true', help='Login to twitter to get tokens')

args = parser.parse_args()

#Get tokens from twitter and save them
if args.login:
    tokens = get_access_token(Config.consumer_key, Config.consumer_secret)

    while True:
        user_input = input('Save tokens to {}? y/n'.format(config_file))
        user_input = user_input.lower()
        if user_input in ['y', 'n']:
            break
        else:
            print('That is not a valid option!')

    if user_input == 'y':
        Config.save_user_tokens(config_file, tokens['token'], tokens['secret'])
        #Reload Config
        Config.load(config_file)



bot = Yatcobot('ignorelist')
bot.run()
