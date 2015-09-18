# twitter-contest-bot
Will poll for Retweet Contests and retweet them. Inspired by http://www.hscott.net/twitter-contest-winning-as-a-service/

A more acceptable use of this kind of app may involve using to search for philanthropic causes requesting retweets, and retweet less often so as not to seem spammy.

[![Build Status](https://travis-ci.org/ModusVivendi/twitter-contest.svg?branch=master)](https://travis-ci.org/ModusVivendi/twitter-contest)

Disclaimer!
------------

This bot is written purely for educational purposes. I hold no liability for what you do with this bot or what happens to you by using this bot. Abusing this bot *can* get you banned from Twitter, so make sure to read up on [proper usage](https://support.twitter.com/articles/76915-automation-rules-and-best-practices) of the Twitter API.

License
------------

You can fork this repository on GitHub as long as it links back to this original repository. Do not sell this script as I would like the code to remain free.

Prerequisites
------------

  * TwitterAPI
  * Python 3.4
  
Configuration
------------

Open up `config.json` and make the values correspond to your Twitter API credentials.

Installation
------------
From the command line:

	pip3 install TwitterAPI
	
Then run:

	python3 main.py

Alternatives
-------------

If you're looking for similar projects in alternative languages, check these out:

* *(JavaScript)* https://github.com/raulrene/Twitter-ContestJS-bot
