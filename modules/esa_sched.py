import willie.module
from os.path import expanduser


def setup(bot):
    global esa_long, esa_short, esa_hdr_long, esa_hdr_short
    # read
    with open("%s/.willie/conf-module/esalong.tsv" % expanduser("~"), "r") as f:
        esa_long = list(f)
    with open("%s/.willie/conf-module/esashort.tsv" % expanduser("~"), "r") as f:
        esa_short = list(f)
    # header
    # split
    esa_hdr_long = esa_long[0].split("\t")
    esa_hdr_short = esa_short[0].split("\t")
    # strip
    hdr = {}
    for i in range(len(esa_hdr_long)):
        if esa_hdr_long[i] and esa_hdr_long[i] != "\n":
            hdr[i] = esa_hdr_long[i]
    esa_hdr_long = hdr
    hdr = {}
    for i in range(len(esa_hdr_short)):
        if esa_hdr_short[i] and esa_hdr_short[i] != "\n":
            hdr[i] = esa_hdr_short[i]
    esa_hdr_short = hdr
    # data
    data = []
    for i in range(1, len(esa_long)):
        line = esa_long[i].split("\t")
        data.append({})
        for linei in range(len(line)):
            if linei in esa_hdr_long:
                data[i - 1][linei] = line[linei]
    esa_long = data
    data = []
    for i in range(1, len(esa_short)):
        line = esa_short[i].split("\t")
        data.append({})
        for linei in range(len(line)):
            if linei in esa_hdr_long:
                data[i - 1][linei] = line[linei]
    esa_short = data


def get_hdr_key(name, which="long"):
    global esa_hdr_long, esa_hdr_short
    name = name.lower()
    hdr = esa_hdr_long if which == "long" else esa_short
    for key in hdr.keys():
        val = hdr[key].lower()
        if name in val:
            return key
    return -1


def find_run(query, group="game", which="long"):
    global data
    query = query.lower()
    hdr_id = get_hdr_key("thing" if which == "short" and group == "game" else group, which)
    data = esa_long if which == "long" else esa_short
    for run in data:
        val = run[hdr_id].lower()
        if query in val:
            return run


def format_run(run):
    # todo store all the keys instead of looking them up each time
    formatted = "\x0309" + run[get_hdr_key("game")] + "\x03"
    if run[get_hdr_key("category")] or run[get_hdr_key("region")]:
        formatted += " (\x0303"
        if run[get_hdr_key("category")]:
            formatted += run[get_hdr_key("category")]
        if run[get_hdr_key("category")] and run[get_hdr_key("region")]:
            formatted += " - "
        if run[get_hdr_key("region")]:
            formatted += run[get_hdr_key("region")]
        formatted += "\x03)"
    if run[get_hdr_key("runner")]:
        formatted += " by \x0312" + run[get_hdr_key("runner")] + "\x03"
    return formatted


@willie.module.commands("esa")
@willie.module.example("esa cur(rent), esa prev(ious), esa next, esa game_name, esa long|short game_name")
@willie.module.rate(10)
def esa(bot, trigger):
    if trigger.group(3) == "cur" or trigger.group(3) == "current":
        pass
    elif trigger.group(3) == "prev" or trigger.group(3) == "previous":
        pass
    elif trigger.group(3) == "next":
        pass
    elif trigger.group(3) == "long" or trigger.group(3) == "short":
        pass
    else:
        query = ""
        try:# are you FUCKING IOGONADOGIN kdidding me
            for i in range(4, 50):
                query += trigger.group(i) + " "
        except:
            pass
        query = query.strip()
        bot.reply(format_run(find_run(query)))
