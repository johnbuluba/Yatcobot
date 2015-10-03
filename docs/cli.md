# Command Line Arguments

Yatcobot supports a number of command line arguments for configuration during
launch

```
usage: yatcobot.py [-h] [--login] [--config CONFIG]
                   [--ignore_list IGNORE_LIST] [--log LOGFILE] [--debug]

Yatcobot: a bot for entering twitter contests

optional arguments:
  -h, --help            show this help message and exit
  --login               Login to twitter to get tokens
  --config CONFIG, -c CONFIG
                        Path of the config file
  --ignore_list IGNORE_LIST, -i IGNORE_LIST
                        Path of the ignore file
  --log LOGFILE         Path of log file
  --debug               Enable debug

```
## -h, --help
Prints help with all the available command line options

## --login
Using the [3-legged authorization](https://dev.twitter.com/oauth/3-legged)
it creates the user access token and access token secret and saves them in
the config file (config.json or any other config file selected, see --config).
For this to work the config file must have the consumer key and secret
(application tokens). This way using one twitter account that has created the
application tokens, multiple user accounts can give permission to the
application to post for them

## --config, -c
**config.json by default**.
The path of the configuration file that will be used. Example usage:
```
./yatcobot.py --config /path/to/config.json
```

## --ignore_list, -i
**ignorelist by default**. The path of the ignore_list file, that stores
the tweets that have been retweeted. Example usage:
```
./yatcobot.py --ignore_list /path/to/ignorelist

```

## --log, -l
Enables logging output to a file. Example usage:
```
./yatcobot.py --log /path/to/out.log

```

## --debug
Enables more verbose output. Used for debug purposes
