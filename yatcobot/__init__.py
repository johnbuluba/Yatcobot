import logging

__version__ = '2.3.2'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def create_logger(level, file=None):
    # Create log outputs
    ch = logging.StreamHandler()

    # Log format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")

    # Set logging format
    ch.setFormatter(formatter)

    # Set level per output

    ch.setLevel(level)

    if file is not None:
        fh = logging.FileHandler(file)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    logger.addHandler(ch)
