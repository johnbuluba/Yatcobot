============
Installation
============


Source
===========

To use from source:

.. code-block:: bash

    sudo apt-get install git python3 python3-pip
    git clone https://github.com/buluba89/Yatcobot.git
    sudo pip3 install -r requirements.txt

Run using:

.. code-block:: bash

    cd /path/to/repo/
    python3 yatcobot.py


Or if you dont want to clutter you global packages use **virualenv**


.. code-block:: bash

    sudo apt-get install git python3 python3-pip python-virtualenv
    git clone https://github.com/buluba89/Yatcobot.git
    cd Yatcobot
    virtualenv -p /usr/bin/python3 env
    source env/bin/activate
    pip3 install -r requirements


And run with

.. code-block:: bash

    cd /path/to/repo/
    source env/bin/activate
    python3 yatcobot.py


For more command line options (See more at :doc:`cli`)


Pip
===

Yatcobot is distributed as a pip package. To install with pip:

.. code-block:: bash
    
    pip3 install yatcobot

Pip installs the package in your PATH you can call *yatcobot* from anywhere



Usage with Docker
=================

To run container use like below

::

    $ docker run -v /path/to/config.yaml:/yatcobot/config.yaml buluba89/yatcobot

where /path/to/config.yaml is the path of your config.json