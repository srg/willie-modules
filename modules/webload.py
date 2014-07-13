# coding=utf-8
"""
downloads module from web to willie/modules/ and loads it
"""
import willie.module, requests, os, imp


@willie.module.nickname_commands("webload")
@willie.module.priority("low")
@willie.module.thread(False)
def webload(bot, trigger):
    if not trigger.admin:
        return

    module_name = trigger.group(2)
    if not module_name or module_name == bot.config.owner:
        return bot.reply("Literally What?")

    format_url = "https://raw.githubusercontent.com/teamsrg/willie/master/willie/modules/{0}.py"
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


# same for pms
@willie.module.commands("webload")
@willie.module.priority("low")
@willie.module.thread(False)
def webload_pm(bot, trigger):
    if trigger.is_privmsg:
        webload(bot, trigger)
