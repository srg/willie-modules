# coding=utf-8
import willie.module, requests
from datetime import datetime


def setup(bot):
    update_races(bot)


@willie.module.thread(True)
def update_races(bot):
    global races_json, races_last_updated
    races_json = requests.get("http://api.speedrunslive.com/races/").json()
    races_last_updated = int(datetime.now().strftime("%s"))


@willie.module.commands("races")
@willie.module.thread(True)
@willie.module.rate(60)
def races(bot, trigger):
    """Notices person a list of all the current races"""
    global races_json, races_last_updated
    if not races_json:
        return
    # if the racelist was last updated over a minute ago
    if int(datetime.now().strftime("%s")) - races_last_updated > 60:
        update_races(bot)
    num = 1
    for i in range(0, int(races_json["count"])):
        r = races_json["races"][i]
        s = int(r["state"])
        if s is 1 or s is 3:
            bot.notice(u"{0}. {1} - {2} | \x0304{3}\x03 | {4} entrants | {5}".format(num, r["game"]["name"], r["goal"], \
                    "#srl-" + r["id"], r["numentrants"], "\x0303Entry Open\x03" if s is 1 else "\x0312In Progress\x03"), \
                    recipient=trigger.nick)
            num += 1
