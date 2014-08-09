import willie, sys, requests, json
from os.path import expanduser

def setup(bot):
    global twitchlist
    f = open("{0}/.willie/conf-module/streams.json".format(expanduser("~"))) # loads streams.json from USER_HOME/.willie/conf-module/
    twitchlist = json.load(f)
    f.close()

@willie.module.commands('streams')
@willie.module.thread(True)
def streams(bot,trigger):
    """Sends the channel a list of currently live streams in a list"""
    global twitchlist
    streamers = []
    online = []
    linelist = []
    counter = 0
    for streamer in twitchlist["streamlist"]:
        streamers.append(streamer + ",")
        streamlist = ''.join(streamers) # make a list of streamers, separated with ',' for our twitch api request
    tw = requests.get('https://api.twitch.tv/kraken/streams?channel=' + streamlist)
    twjson = tw.json()
    hb = requests.get('https://www.hitbox.tv/api/team/speedfriends?filter=&limit=&liveonly=true&media=true') # hitbox srg team support
    hbjson = hb.json()
    for hbstream in hbjson['media']['livestream']: # hitbox.tv \o/
        counter += 1
        online.append("\x037http://hitbox.tv/" + hbstream['media_user_name'] + "\x03 " + hbstream['media_status'] + " \x033|\x03 ")
        if counter % 4 == 0:
            linelist.append(online)
            online = []
    for stream in twjson['streams']:
        if not stream['game']:
            descrip = stream['channel']['status'].rstrip('\n')
        elif len(stream['channel']['status']) < 2: # if the stream title is too short, get the game title instead
            descrip = stream['game']
        else:
             descrip = stream['channel']['status'].rstrip('\n')
        online.append("\x037http://twitch.tv/" + stream['channel']['name'] + " \x03" + descrip + " \x033|\x03 ")
        counter += 1
        if counter % 4 == 0: # have a maximum of 4 streamers per line, the low-ish number is because link + stream titles can get rather long.
            linelist.append(online)
            online = []
    if online: # get the remaining streamers on the last line
        linelist.append(online)
        online = []
    if linelist:
        for line in linelist:
            bot.say(''.join(line)[:-3]) # cut the last 3 characters which are normally used as dividers
    else:
        bot.say(trigger.nick + ": No streams found, go check \x037http://www.twitch.tv/directory/following\x03")
