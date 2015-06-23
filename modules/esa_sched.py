# coding=utf-8

"""
requirements:
- requests
- pytz
"""

import requests
import json
from datetime import timedelta, datetime, tzinfo
import pytz
from os.path import expanduser, getmtime
import willie
from willie.module import thread, commands, interval, rate

MAIN_URL = "http://www.speedrun.com/esa2015/rawschedule/ihfgl" 
SECONDARY_URL = "http://www.speedrun.com/esa2015/rawschedule/jguzf" 
MAIN_START = datetime(2015, 06, 28, 12, 00, tzinfo=pytz.utc) 
SECONDARY_START = datetime(2015, 06, 29, 11, 00, tzinfo=pytz.utc) 
max_runs_per_msg = 2
max_msgs = 3

def setup(bot):
    check_runs(bot, False)

def get_data(url, start):
    j = requests.get(url).json()
    cur_time = 0
    runlist = []
    for entry in j:
        absolute_time = start + timedelta(minutes=cur_time)
        estimate = int(entry["time"])
        cur_time += estimate

        runlist.append({'order':  int(entry["order"]) - 1,
                        'player':  entry["player"],
                        'game':  entry["game"],
                        'category': entry["category"],
                        'console': entry["console"],
                        'absolute_time': absolute_time,
                        'estimate': estimate})
    return runlist

def update_lists():
    global first, second, last_upd
    first = get_data(MAIN_URL, MAIN_START)
    if not first:
        return
    second = get_data(SECONDARY_URL, SECONDARY_START)
    if not second:
        return
    last_upd = datetime.now(pytz.utc)

def get_next(runlist):
    for item in runlist:
        if item["absolute_time"] > datetime.now(pytz.utc):
            return item
            break

def get_prev(runlist):
    for item in runlist:
        if item["absolute_time"] > datetime.now(pytz.utc):
            index = item["order"] - 1
            if index < 0:
                break
            else:
                return runlist[index]
                break

def get_cur(runlist):
    for item in runlist:
        if item["absolute_time"] >= datetime.now(pytz.utc) > runlist[item["order"] + 1]["absolute_time"]:
            return item
        else:
            break

def list_all(runlist):
    for item in runlist:
        print_item(item)

def search_item(term, runlist):
    results = []
    for item in runlist:
        if term.lower() in (item["game"].lower() or item["player"].lower()):
            results.append(item)

@thread(True)
@interval(120)
def check_runs(bot, send_msg=True):
    update_lists()
    update_cur_run(bot)

@interval(120)
def update_cur_run(bot, send_msg=True):
    global first, second, run_cur1, run_cur2
    run_cur_new1 = None
    run_cur_new2 = None
    run_cur1 = get_cur(first)
    run_cur2 = get_cur(second)
    game_old1 = None
    game_old2 = None
    if run_cur1:
        game_old1 = run_cur1["game"]
    if run_cur2:
        game_old2 = run_cur2["game"]
    if game_old1 and run_cur1 != run_cur1["game"]:
        if not send_msg:
            return
        for channel in bot.config.core.get_list("channels"):
            bot.msg(channel, "Game starting: %s" % format_run(run_cur1))
    if game_old2 and run_cur2 != run_cur2["game"]:
        if not send_msg:
            return
        for channel in bot.config.core.get_list("channels"):
            bot.msg(channel, "Game starting: %s" % format_run(run_cur1))

def find_runs(query, key="game", limit=max_runs_per_msg * max_msgs):# limit of 6 should limit it to 2 runs per message, 3 messages
    global first, second
    query = query.lower()
    results = []
    count = 0
    for run in first:
        if query in run[key].lower() and count < limit:
            results.append(run)
            count += 1
        if count is limit:
            break
    for run in second:
        if query in run[key].lower() and count < limit:
            results.append(run)
            count += 1
        if count is limit:
            break
    return results

def format_runs(runs):
    msgs = []
    msg = ""
    pieceofshit = 1
    for run in runs:
        msg += "%s | " % format_run(run, True)
        if pieceofshit is not 0 and pieceofshit % max_runs_per_msg is 0:
            msgs.append(msg[:-3])
            msg = ""
        pieceofshit += 1
    if len(runs) is 1:# top kek >:(
        msgs.append(msg[:-3])
    return msgs

@commands("game", "g")
@rate(5)
def cmd_find_game(bot, trigger):
    query = get_query(trigger)
    if not query:
        bot.say("Usage: !g|game query")
        return
    runs = find_runs(query, key="game")
    if not runs:
        return
    m = format_runs(runs)
    for msg in format_runs(runs):
        bot.say(msg)

@commands("runner", "runners", "r")
@rate(5)
def cmd_find_runner(bot, trigger):
    query = get_query(trigger)
    if not query:
        bot.say("Usage: !r|runner|runners query")
        return
    runs = find_runs(query, key="player")
    if not runs:
        return
    for msg in format_runs(runs):
        bot.say(msg)

@commands("next", "n")
@rate(5)
def cmd_next(bot, trigger):
    global first, second
    next1 = get_next(first)
    next2 = get_next(second)
    send = "The next games are: "
    if next1:
        until1 = time_until(next1)
        msg1 = format_run(next1)
        send += "%s %s (Main stream)" % (msg1, until1)
    if next2:
        if next1:
            send += ", "
        until2 = time_until(next2)
        msg2 = format_run(next2)
        send += "%s %s (Secondary stream)" % (msg2, until2)
    if not (next1 or next2):
        send = "There are no future games."
    bot.say(send)

@commands("prev", "p")
@rate(5)
def cmd_prev(bot, trigger):
    global first, second
    prev1 = get_prev(first)
    prev2 = get_prev(second)
    send = "The previous games were: "
    if prev1:
        ago1 = time_until(prev1)
        msg1 = format_run(prev1)
        send += "%s %s (Main stream)" % (msg1, ago1)
    if prev2:
        if prev1:
            send += ", "
        ago2 = time_until(prev2)
        msg2 = format_run(prev2)
        send += "%s %s (Secondary stream)" % (msg2, ago2)
    if not (prev1 or prev2):
        send = "There have been no games yet."
    bot.say(send)

@commands("cur", "current", "c")
@rate(5)
def cmd_current(bot, trigger):
    global run_cur1, run_cur2
    send = "The current games are: "
    if run_cur1:
        send += "%s (Main stream)" % format_run(run_cur1)
    if run_cur2:
        if run_cur1:
            send += ", "
        send += "%s (Secondary stream)" % format_run(run_cur2)
    if not (run_cur1 or run_cur2):
        send = "There is no current game."
    bot.say(send)

@commands("schedule", "s")
@rate(5)
def cmd_schedule(bot, trigger):
    bot.reply("http://www.speedrun.com/esa2015/doubleschedule")

@commands("update", "upd", "u")
def cmd_update(bot, trigger):
    if not trigger.admin:
        return
    check_runs(bot)

def time_until(item):
    until = item["absolute_time"] - datetime.now(pytz.utc)
    if item["absolute_time"] >= datetime.now(pytz.utc):
        time_until = "[Starts in %s]" % str(until).split('.', 1)[0]
    else:
        time_until = "[%s ago]" % str(until).split('.', 1)[0][1:]
    return time_until

def format_run(item, show_time_until=False):
    estimate = timedelta(minutes=item["estimate"])
    if item["player"] == "????":
        msg = "--- %s [Estimate: %s] ---" % (item["game"], estimate)
    elif item["player"] == "":
        msg = "-- %s [Estimate: %s] --" % (item["game"], estimate)
    elif item["game"] == "Mystery Tournament":
        msg = "-- %s (%s), %s [Estimate: %s] --" % \
              (item["game"], item["category"], item["player"], estimate)
    elif item["category"] == "Tournament finals":
        msg = "-- %s %s, %s [Estimate: %s] --" % \
              (item["game"], item["category"], item["player"], estimate)
    else:
        msg = "%s (%s) by %s [Estimate: %s]" % \
              (item["game"], item["category"], item["player"], estimate)
    if show_time_until:
        msg += " %s" % time_until(item)
    return msg

def get_query(trigger):
    query = trigger.group(0)
    query = query[query.find(trigger.group(1)) + len(trigger.group(1)) + 1:]
    return query.strip()
