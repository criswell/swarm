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
import md5
import tempfile

import swarmlib.config as Config
import swarmlib.log as Log
from swarmlib.db import swarmdb
from swarmlib.db import taxonomy_terms
from swarmlib import master_init
from swarmlib import swarm as Swarm

#import gettext
#gettext.bindtextdomain('swarmlib')
#gettext.textdomain('swarmlib')
#_ = gettext.gettext

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

def cli_parse_datafile(name, column_list):
    """
    Given a datafile (name) and a format for the columns (column_list) will parse
    the file and return a list of the data
    """

    parsed_list = []

    fd = file(name, 'rb')
    for line in fd.readlines():
        temp_line = line.strip()
        if len(temp_line):
            if temp_line[0] != '#':
                temp_split = temp_line.split('|')
                if len(temp_split) == len(column_list):
                    temp_parsed = {}
                    for a in range(len(column_list)):
                        temp_parsed[column_list[a]] = temp_split[a].strip()
                    parsed_list.append(temp_parsed)
                else:
                    logger.error("Unable to parse line, skipping: '%s'" % temp_line)

    return parsed_list

def cli_launch_editor(name):
    """
    Launch an external editor
    Returns:
    (bhash, ahash, bsize, asize)
    Where:
    asize = filesize after
    bsize = filesize before
    ahash = filehash after
    bhash = filehash before
    """

    bstat = os.stat(name)
    bsize = bstat.st_size
    fd = file(name, 'rb')
    bhash = md5.new(fd.read()).digest()
    fd.close()

    # TODO: Right now, we just use $EDITOR from the system environement, but later on
    # we will want to make this fancier
    editor = os.environ.get("EDITOR", "nano")
    cmd = "%s %s" % (editor, name)
    status = os.system(cmd)

    # TODO: Should do something with status

    astat = os.stat(name)
    asize = astat.st_size
    fd = file(name, 'rb')
    ahash = md5.new(fd.read()).digest()
    fd.close()

    return (bhash, ahash, bsize, asize)

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

    master_init(working_dir, log, force)
    logger.unregister()

def cli_taxonomy(pre_options, pre_args, command, post_options):
    verbose = 0
    tax_command = None
    tax_term = 'component'
    working_dir = os.getcwd()

    for o, a in pre_options:
        if o in ("-v", "--verbose"):
            verbose = verbose + 1

    if post_options:
        tax_command = post_options[0]
        if tax_command == 'listall':
            logger.entry('Possible taxonomy terms:', 0)
            for a in taxonomy_terms:
                print "\t%s" % a
            sys.exit()
        if len(post_options) > 1:
            tax_term = post_options[1].lower()
        if len(post_options) == 3:
            working_dir = post_options[2]
    else:
        cli_help(None, None, 'help', ['taxonomy'])
        sys.exit(2)

    log.set_universal_loglevel(verbose)
    logger.register("cli_taxonomy")

    sw = Swarm(working_dir, log)
    components = sw.get_taxonomy(tax_term)

    #FIXME: The following needs to be removed
    # as it's legacy before we had the master swarm
    # abstraction class
    #config = Config.config(working_dir, log)
    #db = swarmdb(working_dir, config, log)
    #db.backend.connect()
    #components = db.backend.get_taxonomy(tax_term)

    if tax_command.lower() == 'list':
        for entry in components:
            print entry
    if tax_command.lower() == 'edit':
        (fp, name) = tempfile.mkstemp()
        temp = os.write(fp,
            "# Entries\n" +
            "# NOTE THAT CHANGING ENTRIES FOR A GIVEN\n" +
            "# 'id' will overwrite that entry globally\n\n" +
            "# FORMAT:\n" +
            "# id | name | details\n")

        for entry in components:
            temp = os.write(fp, "%s | %s | %s\n" % (entry['id'], entry['name'], entry['details']))

        os.close(fp)

        (bhash, ahash, bsize, asize) = cli_launch_editor(name)
        if bhash != ahash:
            new_components = cli_parse_datafile(name, ['id', 'name', 'details'])
            # FIXME: This needs to be removed as well (see above)
            #db.backend.set_taxonomy(tax_term, new_components)
            sw.set_taxonomy(tax_term, new_components)
        else:
            logger.entry("'%s' list unchanged." % tax_term, 0)

        os.remove(name)

    sw.close()
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
    'taxonomy' : Command(
        ['v'],
        ['verbose'],
        'swarm [OPTIONS] taxonomy [TAX COMMAND] [TAX TERM] [DIR]',
        'Perform a taxonomy command',
        ['   Swarm taxonomies define various classifications used to',
         '   categorize issues. Taxonomies may include version,',
         '   milestone, or sub-project information.',
         '',
         '   If a [DIR] is not specified, the current directory is',
         '   used.',
         '',
         '   Every [TAX COMMAND] except for "listall" takes an',
         '   additional option, [TAX TERM], which specifies which',
         '   taxonomy term to perform the operation on',
         '',
         '   The [TAX COMMAND]s are as follows',
         '',
         '   TAX COMMANDS:',
         '   listall        List all the taxonomy terms available',
         '   list           List the current entries in the taxonomy',
         '   edit           Start up an editor and edit the entries',
         '                    in the taxonomy list',
         '',
         '   OPTIONS:',
         '   -v|--verbose   Be verbose about actions',],
        cli_taxonomy),
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
