"""
pip install python-dateutil pytz
"""
import willie.module
from os.path import expanduser
from pytz import timezone
from datetime import datetime
from dateutil import parser


def setup(bot):
    global esa_long, esa_short, esa_hdr_long, esa_hdr_short
    # read
    with open("%s/.willie/conf-module/esalong.tsv" % expanduser("~"), "r") as f:
        esa_long = list(f)
    with open("%s/.willie/conf-module/esashort.tsv" % expanduser("~"), "r") as f:
        esa_short = list(f)
    # header
    esa_hdr_long = parse_tsv_header(esa_long[0])
    esa_hdr_short = parse_tsv_header(esa_short[0])
    # data
    esa_long = dates_to_timestamps(esa_hdr_long, parse_tsv_data(esa_hdr_long, esa_long))
    esa_short = dates_to_timestamps(esa_hdr_short, parse_tsv_data(esa_hdr_short, esa_short))


def dates_to_timestamps(header, runs):
    date_key = header["date"]
    for pos in range(len(runs)):
        if runs[pos]:
            runs[pos][date_key] = int(parser.parse(runs[pos][date_key]).strftime("%s"))
    return runs


def parse_tsv_header(header_line):
    header_line = header_line.split("\t")
    hdr = {}
    for pos in range(len(header_line)):
        if header_line[pos] and header_line[pos] != "\n":
            hdr[header_line[pos].lower()] = pos
    return hdr


def parse_tsv_data(header, data_list):
    data = []
    for list_pos in range(len(data_list)):
        current_list = data_list[list_pos].split("\t")
        data.append({})
        for line_pos in range(len(current_list)):
            if line_pos in header.values():
                data[list_pos - 1][line_pos] = current_list[line_pos]
    return data


def find_run(query, group="game", which="long"):
    global esa_long, esa_short, esa_hdr_long, esa_hdr_short
    query = query.lower()
    hdr_val = esa_hdr_long[group] if which == "long" else esa_hdr_short[group]
    for run in esa_long if which == "long" else esa_short:
        if run and query in run[hdr_val].lower():
            return run
    return None


def find_run_date(trigger, target="current"):
    global esa_long, esa_short, esa_hdr_long, esa_hdr_short
    group = trigger.group()
    runs = esa_long
    hdr_key = esa_hdr_long["date"]
    if " " in group and group[group.index(" ") + 1:] == "short":
        runs = esa_short
        hdr_key = esa_hdr_short["date"] # sure the header keys are the same for both but eh
    time_now = int(datetime.now(timezone("Europe/Stockholm")).strftime("%s"))
    for pos in range(len(runs)):
        if runs[pos][hdr_key] >= time_now:
            if target == "current":
                return runs[pos]
            elif target == "next":
                if pos == len(runs):
                    return None
                return runs[pos + 1]
            else: # previous
                if pos == 0:
                    return None
                return runs[pos - 1]
    return None


def format_run(run, which="long"):
    global esa_hdr_long, esa_hdr_short
    hdr = esa_hdr_long if which == "long" else esa_hdr_short
    formatted = "\x0309" + run[hdr["game"]] + "\x03"
    category = run[hdr["category"]]
    region = run[hdr["region"]]
    runner = run[hdr["runner"]]
    if category or region:
        formatted += " (\x0303"
        if category:
            formatted += category
        if category and region:
            formatted += " - "
        if region:
            formatted += region
        formatted += "\x03)"
    if runner:
        formatted += " by \x0312" + runner + "\x03"
    return formatted


def format_next_run(run, which="long"):
    formatted = format_run(run, which)
    time_now = int(datetime.now(timezone("Europe/Stockholm")).strftime("%s"))
    time_then = run[esa_hdr_long["date"]] if which == "long" else run[esa_hdr_short["date"]]
    seconds = time_then - time_now
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24
    time = ""
    if days > 0:
        time += repr(days) + " days, "
    if hours > 0:
        time += repr(hours % 24) + " hours, "
    if minutes > 0:
        time += repr(minutes % 60) + " mins, "
    time = time[:-2]
    formatted += " in about \x0308" + time + "\x03"
    return formatted


@willie.module.commands("find")
@willie.module.example("find [game|runner] keyword, first parameter is optional and is game by default")
def cmd_find(bot, trigger):
    """
    Returns the first match for keyword of type game or runner in the ESA schedule
    """
    if not trigger.group(3):
        bot.reply("Literally What?")
        return
    group = trigger.group()
    if trigger.group(3) == "runner" and trigger.group(4):
        query = group[group.index(trigger.group(4)):]
        run = find_run(query, "runner")
        if run is None:
            return
        bot.reply(format_run(run))
    else:
        if trigger.group(3) == "game" and trigger.group(4):
            query = group[group.index(trigger.group(4)):]
        else:
            query = group[group.index(trigger.group(3)):]
        run = find_run(query)
        if run is None:
            return
        bot.reply(format_run(run))


@willie.module.commands("cur")
def cmd_current(bot, trigger):
    """
    Returns approximately the current run in the ESA schedule
    """
    run = find_run_date(trigger)
    if run:
        bot.say(format_run(run))
    else:
        bot.reply("Is the event even live yet? :V")


@willie.module.commands("next")
def cmd_next(bot, trigger):
    """
    Returns approximately the next run in the ESA schedule
    """
    run = find_run_date(trigger, "next")
    if run:
        bot.say(format_next_run(run))
    else:
        bot.reply("This is the last run!")


@willie.module.commands("prev")
def cmd_previous(bot, trigger):
    """
    Returns approximately the previous run in the ESA schedule
    """
    run = find_run_date(trigger, "previous")
    if run:
        bot.say(format_run(run))
    else:
        bot.reply("This is the first run!")
