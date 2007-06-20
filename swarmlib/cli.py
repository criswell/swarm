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
import getopt

class Command:
    def __init__(short_opts=None, long_opts=None, usage, summary, desc, callback):
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
        cli_Help),
    'init' : Command(
        ['v', 'f'],
        ['verbose', 'force'],
        '[OPTIONS] init [DEST]',
        'Initialize a swarm DITS repository in given directory',
        ['  Initializes a new swarm DITS repository. Will use the',
         '  [DEST] directory for the new repository, or the current',
         '   directory if nothing is specified.',
         '',
         '  OPTIONS:',
         '  -v|--verbose    Be verbose about actions',
         "  -f|--force      Force even if directory isn't empty"],
         cli_init),
    'help' : Command(
        None,
        None,
        'help [COMMAND]',
        'Gives help for swarm',
        ['   If called with no [COMMAND], will give general help',
         '   and exit. Otherwise, will print help for [COMMAND].'],
         cli_help),
}

def cli_help(pre_options, pre_args, command, post_options):
    if post_options:
        for com in post_options:
            print "\n"
            print option_dispatch[command].usage
            print "\n"
            print option_dispatch[command].summary
            print "\n"
            for line in option_dispatch[command].desc:
                print line
    else:
        print "\n"
        print option_dispatch[None].usage
        print "\n"
        print option_dispatch[None].summary
        print "\n"
        for line in option_dispatch[command].desc:
            print line
        print "\n"
        for com in option_dispatch.keys():
            print "\t%s\t\t" % (com, option_dispatch[com].summary)

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
     for a in option_dispatch[command].short_opts:
         short_opts = short_opts + a

    opts, args = getopt.getopt(pre_opt, short_opts, option_dispatch[command].long_opts)

    return (opts, args, command, post_opt)

def run(argv):
    (pre_options, pre_args, command, post_options)= cli_parse(argv)
    option_dispatch[command].callback(pre_options, pre_args, command, post_options)
