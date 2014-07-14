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
    esa_hdr_long = parse_tsv_header(esa_long[0])
    esa_hdr_short = parse_tsv_header(esa_short[0])
    # data
    esa_long = parse_tsv_data(esa_hdr_long, esa_long)
    esa_short = parse_tsv_data(esa_hdr_short, esa_short)


def parse_tsv_header(header_line):
    header_line = header_line.split("\t")
    hdr = {}
    for pos in range(len(header_line)):
        if header_line[pos] and header_line[pos] != "\n":
            hdr[header_line[pos].lower()] = pos
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

# header long
#     {'category': 3, 'console': 5, 'runner': 7, 'region': 6, 'game': 2, 'date': 1, 'estimate': 4}
# header short
#     {'category': 3, 'console': 5, 'runner\n': 7, 'region': 6, 'game': 2, 'date': 1, 'estimate': 4}
# esa long
#     {1: '27-7-2014 15:10:00', 2: 'Ape Escape 3', 3: 'Any%', 4: '1:45:00', 5: 'PS2', 6: '', 7: 'Cerberus'}
# esa_short
#     {1: '28-7-2014 12:00:00', 2: 'World of Illusion', 3: 'Any% Co-op', 4: '0:30:00', 5: 'Genesis', 6: 'NTSC', 7: 'Edenal & Grukk\n'}

def find_run(query, group="game", which="long"):
    global esa_long, esa_short, esa_hdr_long, esa_hdr_short
    query = query.lower()
    hdr_val = esa_hdr_long[group] if which == "long" else esa_hdr_short[group]
    for run in esa_long if which == "long" else esa_short:
        if run and query in run[hdr_val].lower():
            return run
    return None


def format_run(run, which="long"):
    global esa_hdr_long, esa_hdr_short
    hdr = esa_hdr_long if which == "long" else esa_hdr_short
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


@willie.module.commands("find")
@willie.module.example("find [game|runner] keyword, first parameter is game by default")
def cmd_find(bot, trigger):
    if not trigger.group(3):
        bot.reply("Literally What?")
        return
    group = trigger.group()
    if trigger.group(3) == "runner" and trigger.group(4):
        query = group[group.index(trigger.group(4)):]
        run = find_run(query, "runner")
        if run is None:
            return
        bot.reply(format_run(run))
    else:
        if trigger.group(3) == "game" and trigger.group(4):
            query = group[group.index(trigger.group(4)):]
        else:
            query = group[group.index(trigger.group(3)):]
        run = find_run(query)
        if run is None:
            return
        bot.reply(format_run(run))


@willie.module.commands("cur(rent|ry)?")
def cmd_current(bot, trigger):
    bot.say("oiii")


@willie.module.commands("next")
def cmd_next(bot, trigger):
    bot.say("ayyy")


@willie.module.commands("prev(ious)?")
def cmd_previous(bot, trigger):
    bot.say("lmao")
