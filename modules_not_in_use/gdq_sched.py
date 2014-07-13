# coding=utf-8
"""
requirements:
- requests
- beautifulsoup4
- python-dateutil
"""

disabled = True # kek

import willie.module
import requests
from bs4 import BeautifulSoup
from dateutil import parser
from dateutil.tz import tzoffset
from datetime import datetime


sched = []
sched_url = "http://gamesdonequick.com/schedule"
reverse_lookup = False


def configure(config):
    config.interactive_add("gdq_sched", "update_interval", "GDQ schedule update interval (seconds)", 120)
    config.interactive_add("gdq_sched", "sched_url", "GDQ schedule URL", "http://gamesdonequick.com/schedule")
    config.interactive_add("gdq_sched", "command_rate", "In seconds, the rate of how often a user can execute a command", 5)


def setup(bot):
    if disabled: # kek
        return

    global sched, sched_url

    if not hasattr(update, "interval"):  # set the interval of every how often the schedule should be updated
        interval = 120
        if bot.config.has_option("gdq_sched", "update_interval"):
            interval = int(bot.config.gdq_sched.update_interval)
        update.interval = [interval]

    rate_funcs = [cur_game, next_game, prev_game, find_game]
    for func in rate_funcs:
        if not hasattr(func, "rate"):
            rate = 5
            if bot.config.has_option("gdq_sched", "command_rate"):
                rate = int(bot.config.gdq_sched.command_rate)
            func.rate = rate

    if bot.config.has_option("gdq_sched", "sched_url"):
        sched_url = bot.config.gdq_sched.sched_url
    sched = []

    update()


def update():
    if disabled: # kek
        return

    global sched, sched_url, reverse_lookup
    sched_old = sched
    try:
        sched = []
        html = requests.get(sched_url).text
        bs = BeautifulSoup(html)
        tbody = bs.find("tbody", id="runTable")
        trs = tbody.find_all("tr")
        nowtime = int(datetime.now(tzoffset(None, -21600)).strftime("%s"))
        for pos, tr in enumerate(trs):
            tds = tr.find_all("td")
            if len(tds) is not 8:
                print "gdq_sched.update tds len not 8:", tds
                continue

            runtime = int(parser.parse(tds[0].text + u" -0600").strftime("%s"))
            if runtime >= nowtime and pos >= len(trs) / 2:
                reverse_lookup = True  # implied optimisation for a ~150 item list

            sched.append({"time": runtime, "game": tds[1].text,
                         "runners": tds[2].text, "est": tds[3].text,
                         "setup": tds[4].text, "comments": tds[5].text,
                         "couch": tds[6].text, "prizes": tds[7].text})

        if reverse_lookup:
            sched = list(reversed(sched))
    except Exception, e:
        print "gdq_sched.update exception:", e.message
        sched = sched_old


def cur_game_pos():
    global reverse_lookup

    nowtime = int(datetime.now(tzoffset(None, -21600)).strftime("%s"))
    for pos, run in enumerate(sched):
        if not reverse_lookup and int(run["time"]) >= nowtime or reverse_lookup and int(run["time"]) <= nowtime:
            return pos
    return -1


def format_run(run):
    formatted = "\x0309" + run["game"] + "\x03"
    if run["comments"]:
        formatted += " (\x0303" + run["comments"] + "\x03)"
    formatted += " by \x0310" + run["runners"] + "\x03"
    if run["couch"]:
        formatted += " with \x0310" + run["couch"] + "\x03"
    return formatted


@willie.module.commands("cur", "current", "ongoing", "curry")
def cur_game(bot, trigger):
    if disabled: # kek
        return

    pos = cur_game_pos()
    if pos is -1:
        bot.reply("sry out of runs")
    else:
        bot.reply(format_run(sched[pos]))


@willie.module.commands("next", "upcoming")
def next_game(bot, trigger):
    if disabled: # kek
        return

    global reverse_lookup

    pos = cur_game_pos()
    if pos is -1:
        bot.reply("sry out of runs")
    elif reverse_lookup and pos > 0:
        bot.reply(format_run(sched[pos - 1]))
    elif not reverse_lookup and pos < len(sched):
        bot.reply(format_run(sched[pos + 1]))


@willie.module.commands("prev", "previous")
def prev_game(bot, trigger):
    if disabled: # kek
        return

    global reverse_lookup

    pos = cur_game_pos()
    if pos is -1:
        bot.reply("sry out of runs")
    elif reverse_lookup and pos < len(sched):
        bot.reply(format_run(sched[pos + 1]))
    elif not reverse_lookup and pos > 0:
        bot.reply(format_run(sched[pos - 1]))


@willie.module.commands("find")
def find_game(bot, trigger):
    if disabled: # kek
        return

    if trigger.group(3) != "game" and trigger.group(3) != "runners" and trigger.group(3) != "comments"\
            and trigger.group(3) != "couch":
        bot.reply("usage: .find [game|runners|comments|couch] keyword(s)")
        return

    key = trigger.group(3)
    if key is "":
        key = "game"

    keywords = trigger.group(2)[len(trigger.group(3)) + 1:].lower()
    if len(keywords) < 2:
        return

    count = 0
    runs = ""
    for run in sched:
        if count is 3:  # return the first three hits
            break
        if keywords in run[trigger.group(3)].lower():
            runs += format_run(run) + " | "
            count += 1

    if runs is not "":
        bot.reply(runs[:-3])
