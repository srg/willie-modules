import willie
from math import ceil
from datetime import datetime
from pytz import timezone
from bs4 import BeautifulSoup

def setup(bot):
    get_runs()

@willie.module.thread(True)
def get_run_table(url="https://gamesdonequick.com/schedule"):
    text = ""
    try:
        text = willie.web.get(url, timeout=10, verify_ssl=False)
    except:
        return None
    soup = BeautifulSoup(text)
    table = soup.find(id="runTable")
    return table

# testdate = "1/4/2015 16:55:00"

# @willie.module.commands("setdate")
# def setdate(bot, trigger):
#     global testdate
#     testdate = trigger.group(0)[9:]

# @willie.module.commands("getdate")
# def getdate(bot, trigger):
#     bot.say("testdate='%s'" % testdate)

def parse_runs(run_table):
    if not run_table:
        return None
    date_now = datetime.now(timezone("EST"))
    # date_now = datetime.strptime(testdate, "%m/%d/%Y %H:%M:%S")
    # date_now = date_now.replace(tzinfo = timezone("EST"))
    runs = []
    index = 0

    rows = run_table.find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        if not cols or len(cols) is not 10:
            print "wat"
            continue
        date_run = datetime.strptime(cols[0].text, "%m/%d/%Y %H:%M:%S")# murica time aka EST aka -0500 UTC
        date_run = date_run.replace(tzinfo = timezone("EST"))
        game = cols[1].text
        runners = cols[2].text
        machine = cols[3].text
        estimate = cols[4].text
        # setuptime = cols[5].text
        comments = cols[6].text
        commentators = cols[7].text
        # prizes = cols[8].text
        # twitch = cols[9].text
        date_diff = date_run - date_now
        diff_seconds = ceil(date_diff.total_seconds())
        runs.append({"date": date_run, "seconds_until": diff_seconds,
            "game": game, "runners": runners, "comments": comments,
            "commentators": commentators, "machine": machine,
            "estimate": estimate, "index": index})
        index += 1
    return runs

def get_runs():# todo interval
    global runs
    run_table = get_run_table()
    runs = parse_runs(run_table)
    if not runs:
        return
    set_runs()

def set_runs():
    global runs, run_cur, run_prev, run_next
    the_run = None
    for run in runs:
        sec = run["seconds_until"]
        if sec > 0:
            break
        if not the_run or (sec <= 0 and sec > the_run["seconds_until"]):
            the_run = run
            continue
    run_cur = run_prev = run_next = None
    if the_run:
        run_cur = the_run
    if run_cur and run_cur["index"] > 0:
        run_prev = runs[run_cur["index"] - 1]
    if run_cur and run_cur["index"] < len(runs) - 1:
        run_next = runs[run_cur["index"] + 1]
    elif not run_cur:
        run_next = runs[0]

def find_runs(query, key="game", limit=3):
    query = query.lower()
    results = []
    count = 0
    for run in runs:
        if query in run[key].lower() and count < limit:
            results.append(run)
            count += 1
        if count is limit:
            break
    return results

def time_until(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes,  60)
    days, hours = divmod(hours, 24)
    return (days, hours, minutes)

@willie.module.commands("find", "search")
def cmd_find(bot, trigger):
    key = "game"
    query = trigger.group(0)
    query = query[query.find(trigger.group(1)) + len(trigger.group(1)) + 1:]
    query = query.strip()
    if not query:
        return
    runs = find_runs(query, key=key)
    msg = ""
    for run in runs:
        msg += get_run_info(run)
        if run["seconds_until"] > 0:
            days, hours, mins = time_until(run["seconds_until"])
            msg += " in about \x0312"
            if days:
                msg += "%d days " % days
            if hours:
                msg += "%d hours " % hours
            if mins:
                msg += "%d minutes" % mins
            msg += "\x03"
        msg += " | "
    if len(runs) > 1:
        msg = msg[:-3]
    if msg:
        bot.say(msg)

def get_run_info(run):
    msg = "\x038%s\x03 " % run["game"]
    msg += "(\x037%s" % run["machine"]
    if run["comments"]:
        msg += ", %s" % run["comments"]
    msg += "\x03) "
    msg += "by\x033 %s\x03" % run["runners"]
    if run["commentators"]:
        msg += " (\x0310 %s \x03)" % run["commentators"]
    return msg

@willie.module.commands("cur", "current")
def cmd_current(bot, trigger):
    global run_cur
    if not run_cur:
        return
    bot.say("Current game is %s" % get_run_info(run_cur))

@willie.module.commands("prev", "previous")
def cmd_prev(bot, trigger):
    global run_prev
    if not run_prev:
        return
    bot.say("The previous game was %s" % get_run_info(run_prev))

@willie.module.commands("next")
def cmd_next(bot, trigger):
    global run_next
    if not run_next:
        return
    days, hours, mins = time_until(run_next["seconds_until"])
    msg = ""
    if days:
        msg += "%d days " % days
    if hours:
        msg += "%d hours " % hours
    if mins:
        msg += "%d minutes" % mins
    bot.say("The next game is %s in about \x0312%s\x03" % \
        (get_run_info(run_next), msg))

@willie.module.commands("game")
def cmd_game(bot, trigger):
    if trigger.group(2) == "cur" or trigger.group(2) == "current":
        cmd_current(bot, trigger)
    elif trigger.group(2) == "prev" or trigger.group(2) == "previous":
        cmd_prev(bot, trigger)
    elif trigger.group(2) == "next":
        cmd_next(bot, trigger)

@willie.module.thread(True)
@willie.module.interval(300)# 5 minutes
def check_runs(bot):
    global run_cur
    bot.msg("#fuckbots-dev", "asdf")
    game_cur = run_cur["game"]
    get_runs()
    if game_cur != run_cur["game"]:
        bot.msg("#fuckbots-dev", "New game: %s" % get_run_info(run_cur))
