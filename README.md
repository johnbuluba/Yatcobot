# Yatcobot
The best bot for searching twitter contests and automatically retweet them


[![Build Status](https://travis-ci.org/buluba89/Yatcobot.svg?branch=master)](https://travis-ci.org/buluba89/Yatcobot)
[![codecov.io](http://codecov.io/github/buluba89/Yatcobot/coverage.svg?branch=master)](http://codecov.io/github/buluba89/Yatcobot?branch=master)


Disclaimer!
------------

This bot is written purely for educational purposes. I hold no liability for what you do with this bot or what happens to you by using this bot. Abusing this bot *can* get you banned from Twitter, so make sure to read up on [proper usage](https://support.twitter.com/articles/76915-automation-rules-and-best-practices) of the Twitter API.

License
------------

This program is released under GPL v2


Configuration
------------

Open up `config.json` and make the values correspond to your Twitter API credentials.

**See [Config manual](docs/config.md) for more details**

Installation
------------

#### System wide
___

From the command line:
```
sudo apt-get install git python3 python3-pip
git clone https://github.com/buluba89/Yatcobot.git
sudo pip3 install -r requirements.txt
```
To run:
```
cd /path/to/repo/
python3 yatcobot.py
```

#### Virtualenv
___

From the command line:
```
sudo apt-get install git python3 python3-pip python-virtualenv
git clone https://github.com/buluba89/Yatcobot.git
cd Yatcobot
virtualenv -p /usr/bin/python3 env
source env/bin/activate
pip3 install -r requirements
```
To run:
```
cd /path/to/repo/
source env/bin/activate
python3 yatcobot.py
```
**For options with command line arguments see
[Command Line Arguments!](docs/cli.md)**

## Usage with Docker

To run container use like below

    $ docker run -v /path/to/config.json:/yatcobot/config.json buluba89/yatcobot

where /path/to/config.json is the path of your config.json

Donate
---------
If you want to suppport this project please consider donating with one of the following ways:

  <a href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=buluba89%40gmail%2ecom&lc=GR&item_name=John%20Buluba&currency_code=EUR&bn=PP%2dDonationsBF%3abtn_donate_SM%2egif%3aNonHosted" ><img src="https://www.dokuwiki.org/lib/exe/fetch.php?tok=d9fa04&media=https%3A%2F%2Fraw.githubusercontent.com%2Ftschinz%2Fdokuwiki_paypal_plugin%2Fmaster%2Flogo.jpg" height="24"> </a>

  [![Flattr this git repo](http://api.flattr.com/button/flattr-badge-large.png)](https://flattr.com/submit/auto?user_id=buluba89&url=https://github.com/buluba89/Yatcobot&title=Yatcobot&language=GH_PROJECT_PROG_LANGUAGE&tags=github&category=software)

  <img src="http://www.thisweekintomorrow.com/wp-content/plugins/bitmate-author-donations/images/donate.png" height="24">   *18zSZvVF6XNhg2zi7yvy6fSRnMATc134wm*


Credits
-----------
Based on the work of:
>[ModusVivendi/twitter-contest](https://github.com/ModusVivendi/twitter-contest)


>[kurozael/twitter-contest-bot](https://github.com/kurozael/twitter-contest-bot)
