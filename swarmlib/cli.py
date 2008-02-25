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
import tempfile

import swarmlib.log as Log
import swarmlib.swarm_time as swarm_time
import cli_thread
import cli_util
from swarmlib.db import taxonomy_terms
from swarmlib.swarm import master_init
from swarmlib.swarm import swarm as Swarm

# This would be really nice to include someday
# FIXME
#import gettext
#gettext.bindtextdomain('swarmlib')
#gettext.textdomain('swarmlib')
#_ = gettext.gettext

log = Log.log()
logger = log.get_logger("swarm_cli")

#########################
# Informative Interfaces
#########################

def cli_copyright(pre_options, pre_args, command, post_options):
    """
    Prints the copyright information for Swarm
    """
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

def cli_help(pre_options, pre_args, command, post_options):
    """
    Given a swarm command, will print detailed help for that
    command from the option_dispatch.
    """
    if post_options:
        for com in post_options:
            print option_dispatch[com].usage
            print
            print option_dispatch[com].summary
            print
            for line in option_dispatch[com].desc:
                print line
    else:
        util = cli_util.util(None, log)
        print option_dispatch[None].usage
        print option_dispatch[None].summary
        print
        for line in option_dispatch[None].desc:
            print line
        print
        for com in option_dispatch.keys():
            if com:
                print "   %s%s%s" % (com, util.space_filler(com, 20), option_dispatch[com].summary)

def cli_log(pre_options, pre_args, command, post_options):
    """
    Displays the log information for a hive or a particular issue
    """
    verbose = 0
    working_dir = os.getcwd()
    ticket_number = None

    for o, a in pre_options:
        if o in ("-v", "--verbose"):
            verbose = verbose + 1

    log.set_universal_loglevel(verbose)
    logger.register("cli_log")

    if len(post_options) == 2:
        # swarm log ##### directory
        working_dir = post_options[1]
        ticket_number = post_options[0]
        sw = Swarm(working_dir, log)
    elif len(post_options) == 1:
        # 1) swarm log #####
        # OR
        # 2) swarm log directory
        logger.entry("Ambiguous request, trying local directory for Swarm hive", 0)
        ticket_number = post_options[0]
        sw = Swarm(working_dir, log)
        if not sw.loaded:
            # Try #2
            logger.entry("Local directory not Swarm hive, trying parameter as directory", 0)
            sw.close()
            ticket_number = None
            working_dir = post_options[0]
            sw = Swarm(working_dir, log)
            if not sw.loaded:
                logger.error("Problem accessing Swarm hive '%s'." % working_dir)
    else:
        # Default is to use the last issue
        sw = Swarm(working_dir, log)

    if ticket_number == 0:
        ticket_number = None
    if sw.loaded:
        xlog = sw.get_transaction_log(issue=ticket_number)
        # FIXME
        # This is ugly, was just an early hack that
        # is still around
        for entry in xlog:
            message = "[%i] %s - %s" % (entry[0], swarm_time.human_readable_from_stamp(entry[2]), sw.xactions.dispatch[entry[3]].description)
            if verbose > 0:
                message = message + " : %s" % sw.xactions.dispatch[entry[3]].decode_human_readable(entry[1], entry[4])
            print message
    else:
        logger.error("Problem accessing Swarm hive '%s'." % working_dir)

    sw.close()
    logger.unregister()

def cli_last(pre_options, pre_args, command, post_options):
    """
    Prints the last issue accessed in the hive
    """
    verbose = 0
    working_dir = os.getcwd()

    for o, a in pre_options:
        if o in ("-v", "--verbose"):
            verbose = verbose + 1

    if post_options:
        working_dir = post_options[0]

    log.set_universal_loglevel(verbose)
    logger.register("cli_last")

    sw = Swarm(working_dir, log)
    if sw.config.has_section('cli'):
        last_id = sw.config.get('cli', 'last_issue')
        logger.entry("The last issue was #%s." % last_id, 0)
    else:
        logger.entry("There is no last issue set.", 0)

    sw.close()
    logger.unregister()

#########################
# Utility Interfaces
#########################

def cli_init(pre_options, pre_args, command, post_options):
    """
    Initializes a local hive
    """
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

    master_init(project_name, working_dir, log, force)
    logger.unregister()

def cli_taxonomy(pre_options, pre_args, command, post_options):
    """
    The CLI Taxonomy subcommand interpreter
    """
    verbose = 0
    tax_command = None
    tax_term = 'component'
    working_dir = os.getcwd()

    for o, a in pre_options:
        if o in ("-v", "--verbose"):
            verbose = verbose + 1

    log.set_universal_loglevel(verbose)
    logger.register("cli_taxonomy")

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

    sw = Swarm(working_dir, log)
    components = sw.get_taxonomy(tax_term)
    util = cli_util.util(sw, log)

    if tax_command.lower() == 'list':
        if components:
            for entry in components:
                print entry
        else:
            logger.entry("'%s' is empty." % tax_term, 0)
    if tax_command.lower() == 'edit':
        (fp, name) = tempfile.mkstemp()
        temp = os.write(fp,
            "# Entries\n" +
            "# NOTE THAT CHANGING ENTRIES FOR A GIVEN\n" +
            "# 'id' will overwrite that entry globally\n\n" +
            "# FORMAT:\n" +
            "# id | name | isdefault\n")

        if components:
            for entry in components:
                temp = os.write(fp, "%s | %s | %s\n" % (entry['id'], entry['name'], entry['isdefault']))

        os.close(fp)

        (bhash, ahash, bsize, asize) = util.launch_editor(name)
        if bhash != ahash:
            new_components = util.parse_datafile(name, ['id', 'name', 'isdefault'])
            sw.set_taxonomy(tax_term, new_components)
        else:
            logger.entry("'%s' list unchanged." % tax_term, 0)

        os.remove(name)

    sw.close()
    logger.unregister()

def cli_thread_run(pre_options, pre_args, command, post_options):
    """
    View an issue in a threaded fashion
    """
    verbose = 0
    working_dir = os.getcwd()
    ticket_number = None
    sw = None

    for o, a in pre_options:
        if o in ("-v", "--verbose"):
            verbose = verbose + 1

    log.set_universal_loglevel(verbose)
    logger.register("cli_thread")

    if len(post_options) == 2:
        # swarm thread ##### directory
        working_dir = post_options[1]
        ticket_number = post_options[0]
        sw = Swarm(working_dir, log)
    elif len(post_options) == 1:
        # 1) swarm thread #####
        # OR
        # 2) swarm thread directory
        ticket_number = post_options[0]
        sw = Swarm(working_dir, log)
        if not sw.loaded:
            # Try #2
            sw.close()
            ticket_number = None
            working_dir = post_options[0]
            sw = Swarm(working_dir, log)
    else:
        # Default is to use the last issue
        sw = Swarm(working_dir, log)

    util = cli_util.util(sw, log)

    if sw:
        if sw.loaded:
            if not ticket_number:
                if sw.config.has_section('cli'):
                    ticket_number = sw.config.get('cli', 'last_issue')

            if ticket_number:
                cli_thread.run(sw, log, util, ticket_number)
            else:
                logger.error("No ticket found.")
        else:
            logger.error("No swarm hive found.")

        sw.close()
    logger.unregister()

def cli_new(pre_options, pre_args, command, post_options):
    """
    Create a new issue
    """
    verbose = 0
    working_dir = os.getcwd()

    for o, a in pre_options:
        if o in ("-v", "--verbose"):
            verbose = verbose + 1

    if post_options:
        working_dir = post_options[0]

    log.set_universal_loglevel(verbose)
    logger.register("cli_new")

    sw = Swarm(working_dir, log)
    util = cli_util.util(sw, log)

    schema_issue = sw.get_schema('issue')
    schema_node = sw.get_schema('node')
    (fp, name) = tempfile.mkstemp()
    timestamp = swarm_time.timestamp()
    reporter = sw.get_user()
    temp = os.write(fp,
        "# Create new ticket\n" +
        "#--------------------\n" +
        "# Lines begining with a '#' will be treated as a comment.\n" +
        "# In the header section, blank lines will be ignored\n" +
        "# Lines starting with '@' indicate a section divider.\n\n" +
        "@ HEADER\n\n")
    if schema_issue.has_key('time'):
        temp = os.write(fp, "# timestamp: %s\n" % timestamp)
        temp = os.write(fp, "# %s\n" % swarm_time.human_readable_from_stamp(timestamp))
    if schema_issue.has_key('reporter'):
        temp = os.write(fp, "# reporter: %s\n" % reporter)

    meta_data = ['component', 'version', 'milestone', 'severity', 'priority', 'owner', 'keywords']
    for element in meta_data:
        if schema_issue.has_key(element):
            if element in taxonomy_terms:
                tax = sw.get_taxonomy(element)
                if tax:
                    temp = os.write(fp, "\n# %s, possible values\n# " % element)
                    for item in tax:
                        temp = os.write(fp, "%s: '%s', " % (str(item['id']), str(item['name'])))
                    temp = os.write(fp, "\n")
            temp = os.write(fp, "%s:\n" % element)

    temp = os.write(fp, "\n@ NODE\n")
    meta_data = ['related', 'summary']
    for element in meta_data:
        if schema_node.has_key(element):
            temp = os.write(fp, "%s:\n" % element)

    temp = os.write(fp, "\n# Everything after details (including lines begining with '#' or '@') will\n# be considered part of the details section\n@ DETAILS\n\n")

    os.close(fp)

    (bhash, ahash, bsize, asize) = util.launch_editor(name)
    if bhash != ahash:
        parsed_data = util.parse_issuefile(name, schema_issue, schema_node)
        parsed_data['issue']['time'] = timestamp
        parsed_data['issue']['reporter'] = reporter
        parsed_data['node']['time'] = timestamp
        parsed_data['node']['poster'] = reporter
        new_id = sw.new_issue(parsed_data)
        logger.entry("Ticket #%s has been created." % str(new_id), 0)
        if not sw.config.has_section('cli'):
            sw.config.add_section('cli')
        sw.config.set('cli', 'last_issue', new_id)
        sw.config.save()
    else:
        logger.entry("Ticket creation cancelled.", 0)

    os.remove(name)

    sw.close()
    logger.unregister()

def cli_clone(pre_options, pre_args, command, post_options):
    """
    Clone a hive from a source to the destination
    """
    verbose = 0
    force = False
    to_url = os.getcwd()
    from_url = None

    for o, a in pre_options:
        if o in ("-v", "--verbose"):
            verbose = verbose + 1
        if o in ('-f', '--force'):
            force = True

    log.set_universal_loglevel(verbose)
    logger.register("cli_clone")

    if len(post_options) == 2:
        # clone FROM TO
        from_url = post_options[0]
        to_url = post_options[1]
    elif len(post_options) == 1:
        # clone FROM -- TO is cwd
        from_url = post_options[0]
    else:
        # Wrong number of arguments
        logger.error("clone requires at least one argument. See 'help clone' for more information")

    if from_url and to_url:
        # First, we bootstrap the clone destination
        cli_init(pre_options, pre_args, "cli_init", [to_url])
        sw_to = Swarm(to_url, log)
        # Next, we need a swarm instance for the source
        sw_from = Swarm(from_url, log)
        # Finally, activate the clone
        sw_to.clone(sw_from)

        sw_from.close()
        sw_to.close()

    logger.unregister()

#########################
# Internal Interfaces
#########################

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
        'Initialize a swarm DITS hive in given directory',
        ['  Initializes a new swarm DITS hive. Will use the',
         '  [DEST] directory for the new hive, or the current',
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
    'log' : Command(
        ['v'],
        ['verbose'],
        'swarm [OPTIONS] log [ISSUE] [DIR]',
        'Displays the log (master log or for a given issue)',
        ['  Will display the log. If [ISSUE] is empty (or 0), will',
         '  display the master log for the DITS hive. If',
         '  [ISSUE] is a legitimate issue, will only display the log',
         '  pertaining to it.'
         '',
         '  OPTIONS:',
         '  -v|--verbose    Be verbose about actions'],
        cli_log),
    'last' : Command(
        ['v'],
        ['verbose'],
        'swarm [OPTIONS] last [DIR]',
        'Displays the last ticket modified.',
        ['  Will display the last ticket modified (the current assumed',
         '  ticket if none is specified)',
         '',
         '  OPTIONS:',
         '  -v|--verbose    Be verbose about actions'],
        cli_last),
    'thread' : Command(
        ['v'],
        ['verbose'],
        'swarm [OPTIONS] thread [TICKET_NUMBER] [DIR]',
        'Views the traffic for a given ticket.',
        ['   Will display the ticket traffic for a given ticket',
         '   in threaded format and allow you to add new comments.',
         '',
         '  OPTIONS:',
         '  -v|--verbose    Be verbose about actions'],
        cli_thread_run),
    'new' : Command(
        ['v'],
        ['verbose'],
        'swarm [OPTIONS] new [DIR]',
        'Creates a new ticket.',
        ['   Giving a project workspace (either in current working',
         '   directory or in [DIR]), will create a new ticket. Will',
         '   invoke your editor with the new ticket data and allow',
         '   you to create it.',
         '',
         '  OPTIONS:',
         '  -v|--verbose    Be verbose about actions'],
        cli_new),
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
    'clone' : Command(
        ['v', 'f'],
        ['verbose', 'force'],
        'swarm [OPTIONS] clone [FROM] [TO]',
        'Clones a hive',
        ['   Clones an existing Swarm DITS hive from the [FROM]',
         '   URI to the [TO] URI. If [TO] is not specified, will',
         '   default to the current working directory.',
         '',
         '   OPTIONS:',
         '   -v|--verbose    Be verbose about actions',
         "   -f|--force      Force even if [TO] directory isn't empty"],
        cli_clone),

}

def cli_parse(argv):
    """
    Parse the command line options
    """
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
    """
    The main CLI run trigger
    """
    (pre_options, pre_args, command, post_options)= cli_parse(argv)
    option_dispatch[command].callback(pre_options, pre_args, command, post_options)
