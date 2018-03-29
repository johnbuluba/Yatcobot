===============
Getting Started
===============

Description
===========


| Do you want **free** stuff?
| Do you like do **win**?
| Do you want to participate in twitter **giveaways** but you dont have the time to search and retweet?
| Yatcobot is the solution! A bot that search and retweet giveaways automatically!
|

Features:
---------

Search for new giveaways
  Search and queue tweets to be retweet
Retweet
  `Obviously...`
Advanced sort
   Prioritize tweets found based on parameters like user defined keywords, age and popularity
Notification
   Can notify you using pushbullet when someone mentions you so you can quickly get your precious gift

.. WARNING::
  Your account may be banned for using this kind of bot, so dont use your primary account


Installation
============

The easiest way to install is::

    pip install yatcobot

For more installation methods see (See more at :doc:`installation`)


Configuration
=============
Before starting you must get api keys from twitter. You can get these keys from `here <https://apps.twitter.com/>`_.
(See more at :doc:`api_keys`)

You must create a config named `config.yaml` and must at least set the api keys. A minimal config.yaml is

.. code-block:: yaml

    consumer_key: your_consumer_key
    consumer_secret: your_consumer_secret
    access_token_key: your_access_token
    access_token_secret: your_access_token_secret



Run
===
In the directory where your config.yaml run::

    yatcobot

Or you can specify the path of config with:

    yatcobot --config=/path/to/config.yaml

For more command line options (See more at :doc:`cli`)


You are ready to go
-------------------

Now just wait for all the **free gifts!**









