#!/usr/bin/env python2
# coding=utf-8

"""
requirements:
- requests
- python-dateutil
"""

import requests
import json
from dateutil import parser
from dateutil.tz import tzoffset
from datetime import timedelta, datetime, tzinfo

MAIN_URL = "http://www.speedrun.com/esa2015/rawschedule/ihfgl"
SECONDARY_URL = "http://www.speedrun.com/esa2015/rawschedule/jguzf"
MAIN_START = datetime(2015, 06, 28, 14, 00)
SECONDARY_START = datetime(2015, 06, 29, 13, 00)

def get_data(url, start):
    j = requests.get(url).json()
    cur_time = 0
    runlist = []
    for entry in j:
        # this part is kind of redundant
        order = int(entry["order"]) - 1
        player = entry["player"]
        game = entry["game"]
        category = entry["category"]
        console = entry["console"]

        # this part is ugly
        absolute_time = start + timedelta(minutes=cur_time)
        estimate = int(entry["time"])
        cur_time += estimate

        runlist.append({'order': order,
                                      'player': player,
                                      'game': game,
                                      'category': category,
                                      'console': console,
                                      'absolute_time': absolute_time,
                                      'estimate': estimate})
    return runlist

def get_next(runlist):
    for item in runlist:
        if item["absolute_time"] > datetime.now():
            print_item(item)
            break
        else:
            print "No next run."

def get_prev(runlist):
    for item in runlist:
        if item["absolute_time"] > datetime.now():
            index = item["order"] - 1
            if index < 0:
                print "No previous run."
                break
            else:
                print runlist[index]
                break

def get_cur(runlist):
    for item in runlist:
        if item["absolute_time"] >= datetime.now() > runlist[item["order"] + 1]["absolute_time"]:
            print item
            break
        else:
            print "No current run."
            break

def print_item(item):
    time_until = str(item["absolute_time"] - datetime.now()).split('.', 1)[0]
    if item["player"] == "????":
        print "[Starts in %s] --- %s [Estimate: %s] ---" % (time_until, item["game"], timedelta(minutes=item["estimate"]))
    elif item["player"] == "":
        print "[Starts in %s] -- %s [Estimate: %s] --" % (time_until, item["game"], timedelta(minutes=item["estimate"]))
    elif item["game"] == "Mystery Tournament":
        print "[Starts in %s] -- %s (%s), %s [Estimate: %s] --" % \
                   (time_until, item["game"], item["category"], item["player"], timedelta(minutes=item["estimate"]))
    elif item["category"] == "Tournament finals":
        print "[Starts in %s] -- %s %s, %s [Estimate: %s] --" % \
                  (time_until, item["game"], item["category"], item["player"], timedelta(minutes=item["estimate"]))
    else:
        print "[Starts in %s] %s plays: %s (%s) [Estimate: %s]" % \
                  (time_until, item["player"], item["game"], item["category"], timedelta(minutes=item["estimate"]))

r = get_data(SECONDARY_URL, SECONDARY_START)
get_next(r)
