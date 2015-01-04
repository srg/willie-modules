from math import ceil
from datetime import datetime
from pytz import timezone
from bs4 import BeautifulSoup
import willie
from willie.module import thread, commands, interval, rate

testdate = ""

def setup(bot):
    update_runs()

@thread(True)
def fetch_run_table(url="https://gamesdonequick.com/schedule"):
    text = ""
    try:
        text = willie.web.get(url, timeout=10, verify_ssl=False)
    except:
        return None
    soup = BeautifulSoup(text)
    table = soup.find(id="runTable")
    return table

def parse_run_table(run_table):
    if not run_table:
        return None
    runs = []
    index = 0

    rows = run_table.find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        if not cols or len(cols) is not 10:
            continue
        date_run = datetime.strptime(cols[0].text.strip(), "%m/%d/%Y %H:%M:%S")# murica time aka EST aka -0500 UTC
        date_run = date_run.replace(tzinfo = timezone("EST"))
        game = cols[1].text.strip()
        runners = cols[2].text.strip()
        machine = cols[3].text.strip()
        estimate = cols[4].text.strip()
        # setuptime = cols[5].text.strip()
        comments = cols[6].text.strip()
        commentators = cols[7].text.strip()
        # prizes = cols[8].text.strip()
        # twitch = cols[9].text.strip()
        runs.append({"date": date_run,
            "game": game, "runners": runners, "comments": comments,
            "commentators": commentators, "machine": machine,
            "estimate": estimate, "index": index})
        index += 1
    return runs

def update_runs():
    global runs, run_cur, run_prev, run_next, last_runs_upd
    run_table = fetch_run_table()
    runs_new = parse_run_table(run_table)
    if not runs_new:
        return
    runs = runs_new
    the_run = None
    the_run_diff = -999999
    for run in runs:
        sec = get_time_diff(run)
        if sec > 0:
            break
        if not the_run or (sec <= 0 and sec > the_run_diff):
            the_run = run
            the_run_diff = get_time_diff(the_run)
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
    last_runs_upd = datetime.utcnow()

@thread(True)
@interval(300)# 5 minutes
def check_runs(bot):
    global run_cur
    game_cur = None
    if run_cur:
        game_cur = run_cur["game"]
    update_runs()
    if run_cur and game_cur != run_cur["game"]:
        for channel in bot.config.core.get_list("channels"):
            bot.msg(channel, "Game starting: %s" % format_run(run_cur))

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

def get_time_diff(run, reverse=False):
    date_now = datetime.now(timezone("EST"))
    if testdate:
        date_now = datetime.strptime(testdate, "%m/%d/%Y %H:%M:%S")
        date_now = date_now.replace(tzinfo = timezone("EST"))
    if reverse:
        date_diff = date_now - run["date"]
    else:
        date_diff = run["date"] - date_now
    return ceil(date_diff.total_seconds())

def format_time_diff(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes,  60)
    days, hours = divmod(hours, 24)
    return (days, hours, minutes)

def format_run(run, show_time_until=False):
    msg = "\x0308%s\x03 " % run["game"]
    msg += "(\x0307%s" % run["machine"]
    if run["comments"]:
        msg += ", %s" % run["comments"]
    msg += "\x03) "
    msg += "by \x0303%s\x03" % run["runners"]
    if run["commentators"]:
        msg += " (\x0310%s\x03)" % run["commentators"]
    diff_seconds = get_time_diff(run)
    print diff_seconds
    if show_time_until and diff_seconds > 0:
        days, hours, mins = format_time_diff(diff_seconds)
        msg += " in about \x0312"
        if days:
            msg += "%d days, " % days
        if hours:
            msg += "%d hours, " % hours
        if mins:
            msg += "%d minutes, " % mins
        msg = msg[:-2]
        msg += "\x03"
    elif show_time_until and diff_seconds == 0:
        msg += " \x0312is starting\x03"
    return msg

def format_runs(runs):
    msg = ""
    for run in runs:
        msg += "%s | " % format_run(run, True)
    msg = msg[:-3]
    return msg

def get_query(trigger):
    query = trigger.group(0)
    query = query[query.find(trigger.group(1)) + len(trigger.group(1)) + 1:]
    return query.strip()

@commands("game", "g")
@rate(5)
def cmd_find_game(bot, trigger):
    query = get_query(trigger)
    if not query:
        bot.say("Usage: .g|game query")
        return
    runs = find_runs(query, key="game")
    if runs:
        bot.say(format_runs(runs))

@commands("runner", "runners", "r")
@rate(5)
def cmd_find_runner(bot, trigger):
    query = get_query(trigger)
    if not query:
        bot.say("Usage: .r|runner|runners query")
        return
    runs = find_runs(query, key="runners")
    if runs:
        bot.say(format_runs(runs))

@commands("couch", "commentators")
@rate(5)
def cmd_find_commentators(bot, trigger):
    query = get_query(trigger)
    if not query:
        bot.say("Usage: .couch|commentators query")
        return
    runs = find_runs(query, key="commentators")
    if runs:
        bot.say(format_runs(runs))

@commands("machine", "console", "m")
@rate(5)
def cmd_find_machine(bot, trigger):
    query = get_query(trigger)
    if not query:
        bot.say("Usage: .m|machine|console query")
        return
    runs = find_runs(query, key="machine")
    if runs:
        bot.say(format_runs(runs))

@commands("cur", "current", "c")
@rate(5)
def cmd_current(bot, trigger):
    global run_cur
    if not run_cur:
        return
    bot.say("Current game is %s" % format_run(run_cur))

@commands("prev", "previous", "p")
@rate(5)
def cmd_prev(bot, trigger):
    global run_prev
    if not run_prev:
        return
    bot.say("The previous game was %s" % format_run(run_prev))

@commands("next", "n")
@rate(5)
def cmd_next(bot, trigger):
    global run_next
    if not run_next:
        return
    bot.say("The next game is %s" % format_run(run_next, True))

@commands("schedule", "s")
@rate(5)
def cmd_schedule(bot, trigger):
    bot.reply("https://gamesdonequick.com/schedule")

@commands("help", "h")
@rate(20)
def cmd_help(bot, trigger):
    bot.reply("Usage: .g|game|r|runner|runners|couch|commentators|m|machine|console query, .c|cur|current, .p|prev|previous, .n|next, .s|schedule")

@commands("setdate")
def setdate(bot, trigger):
    if not trigger.admin:
        return
    global testdate
    testdate = trigger.group(0)[9:]

@commands("getdate")
def getdate(bot, trigger):
    if not trigger.admin:
        return
    bot.say("testdate='%s'" % testdate)

@commands("update", "upd", "u")
def cmd_update(bot, trigger):
    if not trigger.admin:
        return
    check_runs(bot)

@commands("last")
def cmd_last_runs_upd(bot, trigger):
    if not trigger.admin:
        return
    global last_runs_upd
    bot.say("Schedule last updated at %s UTC" % last_runs_upd.strftime("%d-%m %H:%M:%S"))
