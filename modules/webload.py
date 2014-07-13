# coding=utf-8
"""
downloads module from web to willie/modules/ and loads it
"""
import willie.module, requests, os, imp, json
from os.path import expanduser

def setup(bot):
    global modulelist
    f = requests.get("https://raw.githubusercontent.com/teamsrg/willie-modules/conf-module/webload.json", stream=True)
    modulelist = json.load(f)
    f.close()

@willie.module.nickname_commands("webload")
@willie.module.priority("low")
@willie.module.thread(False)
def webload(bot, trigger):
    global modulelist
    if not trigger.admin:
        return
    if trigger.group(2) == "list":
        bot.say("Available modules:")
        for mod, val in modulelist["module-list"].items():
            bot.say(mod + ": "  + val)
            
    elif trigger.group(2) == "install":
        module_name = trigger.group(3)
        if not module_name or module_name == bot.config.owner:
            return bot.reply("Literally What?")

        format_url = "https://raw.githubusercontent.com/teamsrg/willie-modules/master/modules/{0}.py"
        module_dir = os.path.dirname(os.path.realpath(__file__))
        with open("{0}/{1}.py".format(module_dir, module_name), "wb") as fh:
            resp = requests.get(format_url.format(module_name), stream=True)
            if resp.status_code is not requests.codes.ok:
                bot.reply("Response code for '{0}' not OK: {1}".format(module_name, resp.status_code))
                return
            for chunk in resp.iter_content(1024):
                if not chunk:
                    break
                fh.write(chunk)
        module = imp.load_source(module_name, "{0}/{1}.py".format(module_dir, module_name))
        if hasattr(module, "setup"):
            module.setup(bot)
        bot.register(vars(module))
        bot.bind_commands()

        bot.reply(module)
    elif not trigger.group(2):
        bot.say("Usage: !weblist list, !weblist install module")

# same for pms
@willie.module.commands("webload")
@willie.module.priority("low")
@willie.module.thread(False)
def webload_pm(bot, trigger):
    if trigger.is_privmsg:
        webload(bot, trigger)
