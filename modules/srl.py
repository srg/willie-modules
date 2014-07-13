# coding=utf-8
import willie.module
import requests

@willie.module.commands("races")
@willie.module.thread(True)
# @willie.module.rate("60")
def races(bot, trigger):
    json = requests.get("http://api.speedrunslive.com/races/").json()
    num = 1
    for i in range(0, int(json["count"])):
        r = json["races"][i]
        s = int(r["state"])
        if s is 1 or s is 3:
            bot.notice(u"{0}. {1} - {2} | \x0304{3}\x03 | {4} entrants | {5}".format(num, r["game"]["name"], r["goal"], \
                    "#srl-" + r["id"], r["numentrants"], "\x0303Entry Open\x03" if s is 1 else "\x0312In Progress\x03"), \
                    recipient=trigger.nick)
            num += 1
