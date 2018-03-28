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

  [![Flattr this git repo](http://api.flattr.com/button/flattr-badge-large.png)](https://flattr.com/submit/auto?user_id=buluba89&url=https://github.com/buluba89/Yatcobot&title=Yatcobot&language=GH_PROJECT_PROG_LANGUAGE&tags=github&category=software)

  [![Donate with Paypal](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=QWCTMJZ9JME3L&lc=GR&item_name=Yatcobot&currency_code=EUR&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted) 
      
  [![Donate with Bitcoin](https://en.cryptobadges.io/badge/small/19iX7wCSzjmr66BY7h3uGRqKWGxuoddjLN)](https://en.cryptobadges.io/donate/19iX7wCSzjmr66BY7h3uGRqKWGxuoddjLN)

  [![Donate with Litecoin](https://en.cryptobadges.io/badge/small/LPzjwWzAPBeUWoeKsusZKEsavkmDS83fRR)](https://en.cryptobadges.io/donate/LPzjwWzAPBeUWoeKsusZKEsavkmDS83fRR)

  [![Donate with Ethereum](https://en.cryptobadges.io/badge/small/0x1c1304173d05c61903789de07a3edcc9629e0222)](https://en.cryptobadges.io/donate/0x1c1304173d05c61903789de07a3edcc9629e0222)

Credits
-----------
Based on the work of:
>[ModusVivendi/twitter-contest](https://github.com/ModusVivendi/twitter-contest)


>[kurozael/twitter-contest-bot](https://github.com/kurozael/twitter-contest-bot)
