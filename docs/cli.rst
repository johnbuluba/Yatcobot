======================
Command Line Arguments
======================

Yatcobot supports a number of command line arguments for configuration
during launch

::

    usage: yatcobot.py [-h] [--login] [--config CONFIG]
                       [--ignore_list IGNORE_LIST] [--log LOGFILE] [--debug]

    Yatcobot: a bot for entering twitter contests

    optional arguments:
      -h, --help            show this help message and exit
      --config CONFIG, -c CONFIG
                            Path of the config file
      --ignore_list IGNORE_LIST, -i IGNORE_LIST
                            Path of the ignore file
      --log LOGFILE         Path of log file
      --debug               Enable debug


-h, --help
    Prints help with all the available command line options


--config, -c
    **config.yaml by default**. The path of the configuration file that will
    be used.

    Example usage:

    ::

        yatcobot --config /path/to/config.yaml


--ignore_list, -i
    **ignorelist by default**. The path of the ignore\_list file,
    that stores the tweets that have been retweeted.

    Example usage:

    ::

        yatcobot.py --ignore_list /path/to/ignorelist

--log, -l
    Enables logging output to a file. Example usage:

    ::

        ./yatcobot --log /path/to/out.log

--debug

    Enables verbose output. Used for debug purposes
