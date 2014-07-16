"""
A module to scrape information from both of the ESA schedules (in the form of tab-separated values)


pip install python-dateutil pytz
"""
import willie.module, requests
from os.path import expanduser
from pytz import timezone
from datetime import datetime
from dateutil import parser


def setup(bot):
    global esa_blue, esa_yellow, esa_hdr_blue, esa_hdr_yellow
    # read
    with open("%s/.willie/conf-module/esablue.tsv" % expanduser("~"), "r") as f:
        esa_blue = list(f)
    with open("%s/.willie/conf-module/esayellow.tsv" % expanduser("~"), "r") as f:
        esa_yellow = list(f)
    # header
    esa_hdr_blue = parse_tsv_header(esa_blue[0])
    esa_hdr_yellow = parse_tsv_header(esa_yellow[0])
    # data
    esa_blue = dates_to_timestamps(esa_hdr_blue, parse_tsv_data(esa_hdr_blue, esa_blue))
    esa_yellow = dates_to_timestamps(esa_hdr_yellow, parse_tsv_data(esa_hdr_yellow, esa_yellow))


def timestamp_swe():
    return int(datetime.now(timezone("Europe/Stockholm")).strftime("%s"))


def timestamp_run(run, which="blue"):
    return run[esa_hdr_blue["date"]] if which == "blue" else run[esa_hdr_yellow["date"]]


def dates_to_timestamps(header, runs):
    date_key = header["date"]
    for pos in range(len(runs)):
        if runs[pos]:
            runs[pos][date_key] = int(parser.parse(runs[pos][date_key], dayfirst=True).strftime("%s"))
    return runs


def parse_tsv_header(header_line):
    header_line = header_line.split("\t")
    hdr = {}
    for pos in range(len(header_line)):
        if header_line[pos] and header_line[pos] != "\n":
            hdr[header_line[pos].lower().encode("utf-8")] = pos
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


def find_run(query, group="game", which="blue"):
    global esa_blue, esa_yellow, esa_hdr_blue, esa_hdr_yellow
    query = query.lower().encode("utf-8")
    hdr_val = esa_hdr_blue[group] if which == "blue" else esa_hdr_yellow[group]
    for run in esa_blue if which == "blue" else esa_yellow:
        if run and query in run[hdr_val].lower():
            return run
    return None


def find_run_date(which="blue", target="cur"):
    global esa_blue, esa_yellow, esa_hdr_blue, esa_hdr_yellow

    runs = esa_blue if which == "blue" else esa_yellow
    hdr_key = esa_hdr_blue["date"] if which == "blue" else esa_hdr_yellow["date"]
    
    time_now = timestamp_swe()
    for pos in range(len(runs)):
        if time_now >= runs[pos][hdr_key]:
            if target == "cur":
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


def format_run(run, which="blue"):
    global esa_hdr_blue, esa_hdr_yellow
    hdr = esa_hdr_blue if which == "blue" else esa_hdr_yellow
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


def format_next_run(run, which="blue"):
    formatted = format_run(run, which)
    time_now = timestamp_swe()
    time_then = timestamp_run(run, which)
    seconds = time_then - time_now
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24
    time = ""
    if days > 0:
        time += repr(days) + " days, "
    if hours % 24 > 0:
        time += repr(hours % 24) + " hours, "
    if minutes % 60 > 0:
        time += repr(minutes % 60) + " mins, "
    time = time[:-2]
    formatted += " in about \x0308" + time + "\x03"
    return formatted


def has_run_happened_yet(run, which="blue"):
    global esa_hdr_blue, esa_hdr_yellow
    time_now = timestamp_swe()
    time_run = timestamp_run(run, which)
    if time_run > time_now:
        return False
    return True


def format_runs(run, run2):
    formatted = format_run(run) if has_run_happened_yet(run, "blue") else format_next_run(run)
    formatted += " | "
    formatted += format_run(run2) if has_run_happened_yet(run2, "yellow") else format_next_run(run2)
    return formatted


@willie.module.commands("find")
@willie.module.example("find [blue|yellow] [game|runner] query, everything except the query is optional and default" + \
        " to blue, game")
def cmd_find(bot, trigger):
    """
    Returns the first match for keyword of type game or runner in one of the ESA schedules
    """
    cmd = trigger.group().encode("utf-8")
    args = cmd.split(" ")
    if len(args) < 2:
        bot.reply("Literally What?")
        return

    which = "both"
    sub_pos = cmd.index(" ") + 1
    if len(args) > 2 and (args[1] == "blue" or args[1] == "yellow"):
        which = args[1]
        sub_pos = cmd.index(args[2])
    
    group = "game"
    if len(args) > 2 and (args[1] == "game" or args[1] == "runner"):
        group = args[1]
        sub_pos = cmd.index(args[2])
    elif len(args) > 3 and (args[2] == "game" or args[2] == "runner") \
            and (args[1] == "blue" or args[1] == "yellow"):
        group = args[2]
        sub_pos = cmd.index(args[3])

    query = cmd[sub_pos:]
    if which == "both":
        run = find_run(query, group, "blue")
        run2 = find_run(query, group, "yellow")
    else:
        run = find_run(query, group, which)
        run2 = None

    if run and run2:
        bot.say(format_runs(run, run2))
    elif run:
        if not has_run_happened_yet(run, which):
            bot.say(format_next_run(run))
        else:
            bot.say(format_run(run))


@willie.module.commands("cur")
@willie.module.commands("next")
@willie.module.commands("prev")
def cmd_current(bot, trigger):
    """
    Returns approximately the previous|current|next run in one of the ESA schedules
    """
    cmd = trigger.group().encode("utf-8")
    target = cmd[1:]
    args = cmd.split(" ")
    
    which = "both"
    if len(args) > 1 and (args[1] == "blue" or args[1] == "yellow"):
        target = target[:target.index(" ")]
        which = args[1]

    bot.reply("cmd:'%s' target:'%s' which:'%s'" % (cmd, target, which))
    bot.reply("swe:'%d'" % timestamp_swe())

    if which == "both":
        run = find_run_date("blue", target)
        bot.reply("run:'%d'" % timestamp_run(run, "blue"))
        run2 = find_run_date("yellow", target)
        bot.reply("run2:'%d'" % timestamp_run(run, "yellow"))
    else:
        run = find_run_date(which, target)
        bot.reply("run:'%d'" % timestamp_run(run, which))
        run2 = None

    if run and run2:
        bot.say(format_runs(run, run2))
    elif run:
        if not has_run_happened_yet(run, which):
            bot.say(format_next_run(run))
        else:
            bot.say(format_run(run))
    else:
        if target == "cur":
            bot.reply("Is the event even live yet? :V")
        elif target == "next":
            bot.reply("This is the last run!")
        elif target == "prev":
            bot.reply("This is the first run!")


@willie.module.commands("esa")
def cmd_update(bot, trigger):
    """
    Redownloads the ESA schedules
    """
    if not trigger.admin or not trigger.group(2):
        return
    if trigger.group(2) == "update":
        blue_url = "https://docs.google.com/spreadsheets/d/1sg3VrOsTlsWkAAFsmYYtadtZoBFZfTvHfy45A8uKgfg/export" + \
                "?format=tsv&id=1sg3VrOsTlsWkAAFsmYYtadtZoBFZfTvHfy45A8uKgfg&gid=723667230"
        yellow_url = "https://docs.google.com/spreadsheets/d/1sg3VrOsTlsWkAAFsmYYtadtZoBFZfTvHfy45A8uKgfg/export" + \
                "?format=tsv&id=1sg3VrOsTlsWkAAFsmYYtadtZoBFZfTvHfy45A8uKgfg&gid=290312202"
        ok = False
        resp = requests.get(blue_url)
        if resp.status_code is requests.codes.ok:
            lines = resp.text.encode("utf-8").split("\n")
            lines[0] = lines[0].replace("Time and date", "Date").replace("Runner/s", "Runner")
            with open("%s/.willie/conf-module/esablue.tsv" % expanduser("~"), "w") as f:
                for line in lines:
                    if line:
                        f.write("%s\n" % line)
            bot.reply("esablue.tsv updated probably")
            ok = True
        else:
            bot.reply("esablue.tsv response code not ok: %d" % resp.status_code)
        resp = requests.get(yellow_url)
        if resp.status_code is requests.codes.ok:
            lines = resp.text.encode("utf-8").split("\n")
            lines[0] = lines[0].replace("Time and date", "Date").replace("Thing", "Game")
            with open("%s/.willie/conf-module/esayellow.tsv" % expanduser("~"), "w") as f:
                for line in lines:
                    if line:
                        f.write("%s\t\n" % line)
            bot.reply("esayellow.tsv updated probably")
            ok = True
        else:
            bot.reply("esayellow.tsv response code not ok: %d" % resp.status_code)
        if ok:
            setup(bot)
    else:
        bot.reply("WU Mot 8?")


@willie.module.commands("schedule")
def cmd_schedule(bot, trigger):
    """
    Returns the URL to the ESA schedule in Google Docs
    """
    bot.reply("https://docs.google.com/spreadsheets/d/1sg3VrOsTlsWkAAFsmYYtadtZoBFZfTvHfy45A8uKgfg/edit")


@willie.module.commands("esas")
@willie.module.commands("esastream")
@willie.module.commands("esastreams")
def cmd_streams(bot, trigger):
    """
    Returns the URL to both of the ESA marathon streams
    """
    bot.reply("Blue: http://twitch.tv/ludendi - Yellow: http://twitch.tv/esa")
