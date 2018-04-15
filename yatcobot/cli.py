import argparse
import logging
import os

from yatcobot import create_logger, __version__
from yatcobot.bot import Yatcobot
from yatcobot.config import TwitterConfig
from yatcobot.plugins.notifiers import MailNotifier

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Yatcobot: a bot for entering twitter contests')
    parser.add_argument('--config', '-c', dest='config', default='config.yaml', help='Path of the config file')
    parser.add_argument('--ignore_list', '-i', dest='ignore_list', default='ignorelist', help='Path of the ignore file')
    parser.add_argument('--log', dest='logfile', default=None, help='Path of log file')
    parser.add_argument('--test-mail', action='store_true', dest='test_mail', default=False, help='Test mail settings')
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
        logger.error("Visit documentation for more info: https://yatcobot.readthedocs.io/en/master/config.html")
        exit(1)

    logger.info("Loading configuration")
    TwitterConfig.load(args.config)
    logger.info("Configuration loaded")

    # Test mail settings and exit
    if args.test_mail:
        MailNotifier.from_config().test()
        exit(1)

    logger.info("Starting Yatcobot ({})".format(__version__))
    print_logo()
    bot = Yatcobot(args.ignore_list)
    bot.run()


def print_logo():
    # Figlet font: Standard
    logger.info(
        '''                                                        
                                  .:clcllcll;.                                  
                                ;xc.        .ld'                                
                              .k:     .'..     xd                               
                              x;    cdcc:cx,    xc                              
                             .WolllxO 0oko.XolllxO                              
                              X,...;0.llo,,O....lO                              
                             l0x    .lllclc     0O;                             
                            OOkOk'            :OOdXl                            
                         .dkK;K' col,.    .;ld, oO:Xdo                          
                         ,o.kWl    :XdX0XOdK.   .xNc.k.                         
                           ,l:    :kO:kOXd:0o,    cl'                           
                                 :O    kl   .K.                                 
                                 .llllllllllll.                                 
                                                                                
                                 _            _           _
                     _   _  __ _| |_ ___ ___ | |__   ___ | |_
                    | | | |/ _` | __/ __/ _ \| '_ \ / _ \| __|
                    | |_| | (_| | || (_| (_) | |_) | (_) | |_
                     \__, |\__,_|\__\___\___/|_.__/ \___/ \__|
                     |___/
 '''
    )
