import willie, sys, json
from os.path import expanduser

def setup(bot):
    global twitchlist
    f = open("{0}/.willie/conf-module/streams.json".format(expanduser("~"))) # loads streams.json from USER_HOME/.willie/conf-module/
    twitchlist = json.load(f)
    f.close()

def lookup_twitch():
    global twitchlist
    twitchers = []
    for twitcher in twitchlist["streamlist"]:
        twitchers.append(twitcher)
    twitchers = ",".join(twitchers)
    try:
        js = willie.web.get("https://api.twitch.tv/kraken/streams?channel=%s" % twitchers, timeout=10, verify_ssl=False)
        return json.loads(js)
    except:# whatever web.get throws and possible valueerror from json.loads
        return None

def lookup_hitbox(team="speedfriends"):
    try:
        js = willie.web.get("https://api.hitbox.tv/team/%s?liveonly=true&media=true" % team, timeout=10, verify_ssl=False)
        return json.loads(js)
    except:# same thing here
        return None

@willie.module.commands("streams")
@willie.module.thread(True)
def streams(bot, trigger):
    tw = lookup_twitch()
    hb = lookup_hitbox()

    msgs = []
    msg = ""
    c = 0

    if hb is not None:
        streams = hb["media"]["livestream"]
        for stream in streams:
            msg += "\x0313https://hitbox.tv/%s\x03 %s \x0313|\x03 " % (stream["media_user_name"], stream["media_status"])
            c += 1
            if c % 4 is 0:
                msgs.append(msg)
                msg = ""

    if tw is not None:
        streams = tw["streams"]
        for stream in streams:
            if len(stream["channel"]["status"]) < 2 and stream["game"]:
                description = stream["game"]
            else:
                description = stream["channel"]["status"].rstrip("\n")
            msg += "\x037http://twitch.tv/%s\x03 %s \x033|\x03 " % (stream["channel"]["name"], description)
            c += 1
            if c % 4 is 0:
                msgs.append(msg)
                msg = ""

    if msg:# add the remaining streams
        msgs.append(msg)

    if not msgs:
        bot.reply("No streams found, try again later")
        return
    for msg in msgs:
        bot.say(msg[:-3])# cut the last 3 characters which are normally used as dividers
