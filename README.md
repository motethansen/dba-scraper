# dba-scraper
python3 based web scraper

This code is an update to the previous scraper written in Python 2.7.

There are some differences on library imports and calls.
To start with, setup the python3 environment:

```bash
$ python3 -m venv env

$ source env/bin/activate
```

We will be using urllib3 to handle the page request. so we have to install the urllib3:

```bash
(env)$ pip install urllib3
```


install the Beautifulsoup package:

```bash
$ pip install beautifulsoup4
```

The URL we are looking at is from a danish website DBA:

https://www.dba.dk/brugerens-annoncer/brugerid-5683282/
---
