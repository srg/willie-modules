#!/usr/bin/env python2
# coding=utf-8

"""
requirements:
- requests
"""

import requests
import json
from datetime import timedelta, datetime, tzinfo

MAIN_URL = "http://www.speedrun.com/esa2015/rawschedule/ihfgl"
SECONDARY_URL = "http://www.speedrun.com/esa2015/rawschedule/jguzf"
MAIN_START = datetime(2015, 06, 28, 14, 00)
SECONDARY_START = datetime(2015, 06, 29, 13, 00)

def get_url(url, start):
    j = requests.get(url).json()
    cur_time = 0
    for entry in j:
        # this part is kind of redundant
        order = int(entry["order"]) - 1
        player = entry["player"]
        game = entry["game"]
        category = entry["category"]
        console = entry["console"]

        # this part is ugly
        absolute_time = start + timedelta(minutes=cur_time)
        time_until = absolute_time - datetime.now()
        estimate = int(entry["time"])
        cur_time += estimate

        print "[Starts in %s] %s plays: %s [Estimate: %s]" % (str(time_until).split('.', 1)[0], player, game, timedelta(minutes=estimate))


get_url(SECONDARY_URL, SECONDARY_START)
