LUNA stats to external stat server relay
========================================

Requirements
------------

* python3.6
* virtualenv

Installation
------------

`python3.6 -m venv venv`

`source myvenv/bin/activate`

`pip install -r requirements.txt`

`python3.6 server.py`

Configuration
-------------

To override default settings, you should crate config.json file in project folder.

See `config.example.json` for list and description of params

Running
-------

Script could be started using any supervisor (systemd, initctl, supervisord, etc).

Run command could looks like `/path/to/myvenv/bin/python /path/to/project/server.py`

Working directory should be set to `/path/to/project/`