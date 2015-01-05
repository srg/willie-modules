# coding=utf-8
"""
downloads module from web to willie/modules/ and loads it
"""
import willie.module, requests, os, imp, json, types
from os.path import expanduser

def setup(bot):
    global modulelist
    modulelist = requests.get("https://raw.githubusercontent.com/srg/willie-modules/master/conf-module/webload.json").json()
    global williedir
    williedir = os.path.dirname(os.path.realpath(__file__ + "/../"))
    print williedir


def getdepends(depend, format_url, bot):
    abort_mission = 0
    dependresp = requests.get(format_url + depend, stream=True)
    if dependresp.status_code is not requests.codes.ok:
        bot.reply("Respondse code for '{0}' not OK: {1}".format(dependresp, dependresp.status_code))
        abort_mission = 1
        return
    if abort_mission:
        return
    with open("{0}/{1}".format(williedir, depend), "wb") as fd:
        for chunk in dependresp.iter_content(1024):
            if not chunk:
                break
            fd.write(chunk)

    
def sync(bot, module_name):
    global williedir
    global modulelist
    if not module_name or module_name == bot.config.owner:
        return bot.reply("No such module, use !webload list for available modules.")
    format_url = "https://raw.githubusercontent.com/srg/willie-modules/master/"
    resp = requests.get(format_url + "modules/" + module_name + ".py", stream=True)
    if resp.status_code is not requests.codes.ok:
        bot.reply("Response code for '{0}' not OK: {1}".format(module_name, resp.status_code))
        return
    with open("{0}/modules/{1}.py".format(williedir, module_name), "wb") as fh:
        for chunk in resp.iter_content(1024):
            if not chunk:
                break
            fh.write(chunk)
    if modulelist[module_name]["depends"]:
        depends = modulelist[module_name]["depends"]
        if isinstance(depends, basestring):
            getdepends(depends, format_url, bot)
        else:
            for depen in depends:
                getdepends(depen, format_url, bot)
    module = imp.load_source(module_name, "{0}/modules/{1}.py".format(williedir, module_name))
    if hasattr(module, "setup"):
        module.setup(bot)
    bot.register(vars(module))
    bot.bind_commands()
    bot.reply(module)


@willie.module.nickname_commands("webload")
@willie.module.priority("low")
@willie.module.example("webload list, webload sync, webload update")
@willie.module.thread(True)
def webload(bot, trigger):
    """Does the same thing as 'reload.load' except loads the module from the repository"""
    global williedir
    global modulelist
    if not trigger.admin:
        return
    if trigger.group(3) == "list":
        bot.say("Available modules:")
        for mod, val in modulelist.items():
            if os.path.isfile(williedir + "/modules/" + mod + ".py"):
                comment = val["comment"] + " \x03[installed]"
            else:
                comment = val["comment"]
            bot.say("[\x033" + val["state"] + "\x03] \x037" + mod + ": \x0312"  + comment)
    elif trigger.group(3) == "sync":
        sync(bot, trigger.group(4))
    elif trigger.group(3) == "update":
        for mod, val in modulelist.items():
            if os.path.isfile(williedir + "/modules/" + mod + ".py"):
                sync(bot, mod)
    elif trigger.group(3) == "remove":
        removethis = williedir + "/modules/" + trigger.group(4)
        if os.path.isfile(removethis + ".py"):
            os.remove(removethis + ".py")
            os.remove(removethis + ".pyc")
            bot.say("\x037" + trigger.group(4) + "\x03 removed. You should probably restart the bot.")
            # bad idea, i don't want to advertise it too much
        else:
            bot.say("fug of :-D")
    elif not trigger.group(3):
        bot.say("Usage: !weblist list, !weblist sync module, !weblist update. use !weblist remove at your own discretion.")

# same for pms
@willie.module.commands("webload")
@willie.module.priority("low")
@willie.module.thread(False)
def webload_pm(bot, trigger):
    if trigger.is_privmsg:
        webload(bot, trigger)
