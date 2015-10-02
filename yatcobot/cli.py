#!/usr/bin/env python3
import argparse
import logging
from yatcobot import create_logger
from yatcobot.bot import Yatcobot
from yatcobot.token_getter import get_access_token
from yatcobot.config import Config


def main():
    parser = argparse.ArgumentParser(description='Yatcobot: a bot for entering twitter contests')
    parser.add_argument('--login', dest='login', action='store_true', help='Login to twitter to get tokens')
    parser.add_argument('--config', '-c', dest='config', default='config.json', help='Path of the config file')
    parser.add_argument('--ignore_list', '-i', dest='ignore_list', default='ignorelist', help='Path of the ignore file')
    parser.add_argument('--log', dest='logfile', default=None, help='Path of log file')
    parser.add_argument('--debug', dest='debug', action='store_true', help='Enable debug')

    args = parser.parse_args()

    #Gets user tokens from twitter and saves them
    if args.login:
        tokens = get_access_token(Config.consumer_key, Config.consumer_secret)

        while True:
            user_input = input('Save tokens to {}? y/n '.format(args.config))
            user_input = user_input.lower()
            if user_input in ['y', 'n']:
                break
            else:
                print('That is not a valid option!')

        if user_input == 'y':
            Config.save_user_tokens(args.config, tokens['token'], tokens['secret'])

    #Create logger
    if args.debug:
        create_logger(logging.DEBUG, args.logfile)
    else:
        create_logger(logging.INFO, args.logfile)


    Config.load(args.config)

    bot = Yatcobot(args.ignore_list)
    bot.run()
