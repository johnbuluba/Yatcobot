import argparse
import logging
import os

from yatcobot import create_logger
from yatcobot.bot import Yatcobot
from yatcobot.config import TwitterConfig

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Yatcobot: a bot for entering twitter contests')
    parser.add_argument('--config', '-c', dest='config', default='config.yaml', help='Path of the config file')
    parser.add_argument('--ignore_list', '-i', dest='ignore_list', default='ignorelist', help='Path of the ignore file')
    parser.add_argument('--log', dest='logfile', default=None, help='Path of log file')
    parser.add_argument('--debug', dest='debug', action='store_true', help='Enable debug')

    args = parser.parse_args()

    # Create logger
    if args.debug:
        create_logger(logging.DEBUG, args.logfile)
    else:
        create_logger(logging.INFO, args.logfile)

    # Check for old config
    if args.config.endswith('.json') or (os.path.isfile('config.json') and not os.path.isfile('config.yaml')):
        logger.error("Config file format changed, please update your config to the new yaml format!")
        exit(1)

    TwitterConfig.load(args.config)
    bot = Yatcobot(args.ignore_list)
    bot.run()
