import willie, requests, re

@willie.module.commands('thread')
@willie.module.thread(True)
def thread(bot, trigger):
    """Sends the channel the link to the current /srg/ thread"""
    r = requests.get('http://a.4cdn.org/vg/catalog.json')
    jason = r.json()
    found = 0
    for idx, val in enumerate(jason):
        for idx2, val2 in enumerate(jason[idx]['threads']):
            threads = jason[idx]['threads'][idx2]
            if re.search("se?rg", threads['sub'].lower()):
                threadnum = threads['no']
                found = 1
                break
        if found == 1:
            break
    if found == 1:
        bot.say(trigger.nick +": \x037http://boards.4chan.org/vg/thread/%d\x03" % (threadnum))
    else:
        bot.say(trigger.nick + ": Thread not found, check \x037http://4chan.org/vg/srg\x03")
