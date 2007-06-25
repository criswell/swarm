#!/usr/bin/env python

# Copyright 2007 Sam Hart
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Author: Sam Hart

import sys
import os
import getopt
import swarmlib.config as Config
import swarmlib.log as Log
from swarmlib.db import swarmdb

log = Log.log()
logger = log.get_logger("swarm_cli")

def cli_copyright(pre_options, pre_args, command, post_options):
    print " Swarm DITS\n"

    print " Copyright 2007 Sam Hart\n"

    print " This program is free software; you can redistribute it and/or modify"
    print " it under the terms of the GNU General Public License as published by"
    print " the Free Software Foundation; either version 2 of the License, or"
    print " (at your option) any later version.\n"

    print " This program is distributed in the hope that it will be useful,"
    print " but WITHOUT ANY WARRANTY; without even the implied warranty of"
    print " MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the"
    print " GNU General Public License for more details.\n"

    print " You should have received a copy of the GNU General Public License"
    print " along with this program; if not, write to the Free Software"
    print " Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA"

def cli_space_filler(command, size):
    a = " "
    if size > len(command):
        a = " " * (size - len(command))
    return a

def cli_help(pre_options, pre_args, command, post_options):
    if post_options:
        for com in post_options:
            print option_dispatch[com].usage
            print
            print option_dispatch[com].summary
            print
            for line in option_dispatch[com].desc:
                print line
    else:
        print option_dispatch[None].usage
        print option_dispatch[None].summary
        print
        for line in option_dispatch[None].desc:
            print line
        print
        for com in option_dispatch.keys():
            if com:
                print "   %s%s%s" % (com, cli_space_filler(com, 20), option_dispatch[com].summary)

def cli_init(pre_options, pre_args, command, post_options):
    verbose = 0
    force = False
    working_dir = os.getcwd()
    project_name =  os.path.split(working_dir)[-1]
    if post_options:
        working_dir = post_options[0]
        project_name = working_dir

    for o, a in pre_options:
        if o in ("-v", "--verbose"):
            verbose = verbose + 1
        if o in ("-f", "--force"):
            force = True

    log.set_universal_loglevel(verbose)
    logger.register("cli_init")
    logger.entry("Initializing directory '%s'" % working_dir, 0)

    config = Config.config(working_dir, log, force)
    config.init(project_name)
    db = swarmdb(working_dir, config, log, force)
    db.backend.init()
    db.backend.close()
    logger.unregister()

def cli_component(pre_options, pre_args, command, post_options):
    verbose = 0
    comp_command = None
    working_dir = os.getcwd()

    for o, a in pre_options:
        if o in ("-v", "--verbose"):
            verbose = verbose + 1

    if post_options:
        comp_command = post_options[0]
    else:
        cli_help(None, None, 'help', ['component'])
        sys.exit(2)

    log.set_universal_loglevel(verbose)
    logger.register("cli_component")

    config = Config.config(working_dir, log)
    db = swarmdb(working_dir, config, log)
    db.backend.connect()

    if comp_command.lower() == 'list':
        components = db.backend.get_taxonomy('severity') #('component')

    db.backend.close()
    logger.unregister()


class Command:
    def __init__(self, short_opts, long_opts, usage, summary, desc, callback):
        self.short_opts = short_opts
        self.long_opts = long_opts
        self.usage = usage
        self.summary = summary
        self.desc = desc
        self.callback = callback

# Defines
option_dispatch = {
    None : Command(
        None,
        None,
        'Swarm DITS',
        'Swarm Distributed Issue Tracking System',
        ['basic commands, use "help" to get more details.'],
        cli_help),
    'init' : Command(
        ['v', 'f'],
        ['verbose', 'force'],
        'swarm [OPTIONS] init [DEST]',
        'Initialize a swarm DITS repository in given directory',
        ['  Initializes a new swarm DITS repository. Will use the',
         '  [DEST] directory for the new repository, or the current',
         '   directory if nothing is specified.',
         '',
         '  OPTIONS:',
         '  -v|--verbose    Be verbose about actions',
         "  -f|--force      Force even if directory isn't empty"],
        cli_init),
    'component' : Command(
        ['v'],
        ['verbose'],
        'swarm [OPTIONS] component [COMP COMMAND]',
        'Perform a "component" command',
        ['   Components are sub-project classifications which issues',
         '   can be filed against. The [COMP COMMAND]s are as follows',
         '',
         '   COMP COMMANDS:',
         '   list           List the current components',
         '   edit           Start up an editor and edit the component',
         '                      list',
         '   add [COMP]     Add a new component to the list',
         '   delete [COMP]  Delete a component from the list',
         '',
         '   OPTIONS:',
         '   -v|--verbose   Be verbose about actions',],
        cli_component),
    'help' : Command(
        None,
        None,
        'swarm help [COMMAND]',
        'Gives help for swarm',
        ['   If called with no [COMMAND], will give general help',
         '   and exit. Otherwise, will print help for [COMMAND].'],
         cli_help),
    'copyright' : Command(
        None,
        None,
        'Swarm DITS',
        'Swarm copyright notice',
        ['Copyright (C) 2006 Sam Hart\n','This program is free software; you can redistribute it and/or modify',
         'it under the terms of the GNU General Public License.'],
        cli_copyright),

}

def cli_parse(argv):
    pre_opt = []
    command = None
    post_opt = []
    stage = 0
    for option in argv:
        if stage == 0:
            if option in option_dispatch.keys():
                stage = 1
                command = option
            else:
                pre_opt.append(option)
        else:
            post_opt.append(option)

    short_opts = ''
    long_opts = []
    if option_dispatch[command].short_opts:
        for a in option_dispatch[command].short_opts:
            short_opts = short_opts + a

    if option_dispatch[command].long_opts:
        long_opts = option_dispatch[command].long_opts

    opts, args = getopt.getopt(pre_opt, short_opts, long_opts)

    return (opts, args, command, post_opt)

def run(argv):
    (pre_options, pre_args, command, post_options)= cli_parse(argv)
    option_dispatch[command].callback(pre_options, pre_args, command, post_options)
