# coding=utf8
"""
help.py - Willie Help Module
Copyright 2008, Sean B. Palmer, inamidst.com
Copyright © 2013, Elad Alfassa, <elad@fedoraproject.org>
Licensed under the Eiffel Forum License 2.

http://willie.dftba.net
"""
from __future__ import unicode_literals

from willie.module import commands, rule, example, priority
from willie.tools import iterkeys


def setup(bot):
    global admin_only
    admin_only = ["blocks", "join", "load", "me", "mode", "msg", "part", "quit", "reload", "save", "set", "update", "webload"]


@rule('$nick' '(?i)(help|doc) +([A-Za-z]+)(?:\?+)?$')
@example('.help tell')
@commands('help')
@priority('low')
def help(bot, trigger):
    """Shows a command's documentation, and possibly an example."""
    global admin_only
    if not trigger.group(2):
        bot.reply('Say .help <command> (for example .help c) to get help for a command, or .commands for a list of commands.')
    else:
        name = trigger.group(2)
        name = name.lower()

        if name in bot.doc and name not in admin_only:
            bot.reply(bot.doc[name][0])
            if bot.doc[name][1]:
                bot.say('e.g. ' + bot.doc[name][1])


@commands('commands')
@priority('low')
def commands(bot, trigger):
    """Return a list of bot's commands"""
    global admin_only
    names_list = sorted(iterkeys(bot.doc))
    names_list_send = []
    for i in range(len(names_list)): # sketchy as shit
        name = names_list[i]
        if name in admin_only and trigger.admin:
            names_list_send.append("\x0312%s\x03" % name)
        elif name not in admin_only and trigger.admin:
            names_list_send.append("\x0309%s\x03" % name)
        elif name not in admin_only:
            names_list_send.append(name)
    names = ', '.join(names_list_send)
    if not trigger.is_privmsg:
        bot.reply("I am sending you a private message of all my commands!")
    bot.msg(trigger.nick, 'Commands I recognise: ' + names + '.', max_messages=10)
    bot.msg(trigger.nick, ("For help, do '%s: help example' where example is the " +
                    "name of the command you want help for.") % bot.nick)
