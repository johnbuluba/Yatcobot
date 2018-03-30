===============
Getting Started
===============

.. figure:: https://thumb.ibb.co/hLfUvS/Screenshot_from_2018_03_30_04_47_49.png
  :height: 100px
  :alt: logo
  :align: right

*The best bot for retweeting twitter giveaways!*


|Build Status| |codecov.io|


| Do you want **free** stuff?
| Do you like do **win**?
| Do you want to participate in twitter **giveaways** but you dont have the time to search and retweet?
| Yatcobot is the solution! A bot that search and retweet giveaways automatically!
|

Features:
---------

- **Search for new giveaways** 
  *Search and queue tweets to retweet, with a customizable way*

- **Retweet** 
  *Obviously...*

- **Advanced sort** 
  *Prioritize tweets found based on parameters like user defined keywords, age and popularity*

- **Notification**
  *Can notify you using pushbullet when someone mentions you so you can quickly get your precious gift*

----

You can visit <https://readthedocs.org/projects/yatcobot/>`_ for extended documentation or
follow these steps for a quick start

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
In the directory where your config.yaml run:

.. code-block:: bash

    yatcobot

Or you can specify the path of config with:

.. code-block:: bash

    yatcobot --config=/path/to/config.yaml

For more command line options (See more at :doc:`cli`)


Now just wait for all the **free gifts!**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


----



Documentation
=============
For more info visit our docs: `<https://readthedocs.org/projects/yatcobot/>`_.

----

Donate
======

Please donate to support the development if you find this software useful (`or if you are so rich from the staff you won`).


|Flattr this git repo|

|Donate with Paypal|

|Donate with Bitcoin|

|Donate with Litecoin|

|Donate with Ethereum|


.. |Flattr this git repo| image:: http://api.flattr.com/button/flattr-badge-large.png
   :target: https://flattr.com/submit/auto?user_id=buluba89&url=https://github.com/buluba89/Yatcobot&title=Yatcobot&language=GH_PROJECT_PROG_LANGUAGE&tags=github&category=software
.. |Donate with Paypal| image:: https://img.shields.io/badge/Donate-PayPal-green.svg
   :target: https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=QWCTMJZ9JME3L&lc=GR&item_name=Yatcobot&currency_code=EUR&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted
.. |Donate with Bitcoin| image:: https://en.cryptobadges.io/badge/small/19iX7wCSzjmr66BY7h3uGRqKWGxuoddjLN
   :target: https://en.cryptobadges.io/donate/19iX7wCSzjmr66BY7h3uGRqKWGxuoddjLN
.. |Donate with Litecoin| image:: https://en.cryptobadges.io/badge/small/LPzjwWzAPBeUWoeKsusZKEsavkmDS83fRR
   :target: https://en.cryptobadges.io/donate/LPzjwWzAPBeUWoeKsusZKEsavkmDS83fRR
.. |Donate with Ethereum| image:: https://en.cryptobadges.io/badge/small/0x1c1304173d05c61903789de07a3edcc9629e0222
   :target: https://en.cryptobadges.io/donate/0x1c1304173d05c61903789de07a3edcc9629e0222
.. |Build Status| image:: https://travis-ci.org/buluba89/Yatcobot.svg?branch=master
   :target: https://travis-ci.org/buluba89/Yatcobot
.. |codecov.io| image:: https://codecov.io/gh/buluba89/Yatcobot/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/buluba89/Yatcobot

