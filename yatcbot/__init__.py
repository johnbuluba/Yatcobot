import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

#Create log outputs
fh = logging.FileHandler('log')
ch = logging.StreamHandler()

#Log format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

#Set logging format
fh.setFormatter(formatter)
ch.setFormatter(formatter)

#Set level per output
fh.setLevel(logging.DEBUG)
ch.setLevel(logging.INFO)

logger.addHandler(fh)
logger.addHandler(ch)
