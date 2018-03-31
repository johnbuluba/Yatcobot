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
        logger.error("Visit documentation for more info: https://yatcobot.readthedocs.io/en/master/config.html")
        exit(1)

    logger.info("Loading configuration")
    TwitterConfig.load(args.config)
    logger.info("Configuration loaded")
    logger.info("Starting")
    print_logo()
    bot = Yatcobot(args.ignore_list)
    bot.run()


def print_logo():
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
                                                                                
                                                   ';                           
                       cd                          o0                   'O      
 'K.    Oc  cOlcdO.   cXKccc    dxccok'  .xdccxk.  oXcclkk   ,koclkl   ;ONccc.  
  ;K.  Ok   .',;;Xl    Ok      dX    .   OO    0k  oX    Kl .N:   .W;   oK      
   lK.dO   .No'..Xl    Ok      xX    ..  OO    OO  oK    Kl .W;   .W;   oK      
    oX0    .No,:l0O.   oK;,;.  .Ok;,lK;  .0d,,x0.  oNo;,xK.  :0c,:Ox    ;N:,,.  
    ;X.      .'.  '.    .''.     ..'.      .''.     . .'.      .'.       .''. 
        
        '''
    )
