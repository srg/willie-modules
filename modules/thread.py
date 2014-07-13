import willie, requests

@willie.module.commands('thread')

def thread(bot, trigger):
    r = requests.get('http://a.4cdn.org/vg/catalog.json')
    jason = r.json()
    found = 0
    for idx, val in enumerate(jason):
        for idx2, val2 in enumerate(jason[idx]['threads']):
            threads = jason[idx]['threads'][idx2]
            if "srg" in threads['sub'].lower(): # this will find 'srg' in the title field and return thread number ID of the first thread/with most recent activity
                threadnum = threads['no']
                found = 1
                break
        if found == 1:
            break
    if found == 1:
        bot.say(trigger.nick +": \x037http://boards.4chan.org/vg/thread/%d\x03" % (threadnum))
    else:
        bot.say(trigger.nick + ": Thread not found, check \x037http://4chan.org/vg/srg\x03")
