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
import swarmlib.swarm_time as swarm_time
from swarmlib.db import swarmdb
from swarmlib.db import taxonomy_terms
from swarmlib.swarm import master_init
from swarmlib.swarm import swarm as Swarm

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

    fd.close()
    return parsed_list

def cli_parse_issuefile(name, schema_issue, schema_node):
    """
    cli_parse_issuefile(name, schema_issue, schema_node)
    Given a issue file(name) and the schemas for issues and nodes,
    will parse the issuefile and return a hash containing the parsed
    issue data.
    returned_data = {'issue': {parsed data}, 'node': {parsed data}}
    """
    parsed_data = {'issue': {}, 'node': {}}
    for column in schema_issue:
        parsed_data['issue'][column] = None

    for column in schema_node:
        parsed_data['node'][column] = None

    parsed_data['node']['details'] = ""

    current_section = None

    fd = file(name, 'rb')
    for line in fd.readlines():
        temp_line = line.strip()
        if current_section == 'details':
            parsed_data['node']['details'] = parsed_data['node']['details'] + temp_line.strip() + "\n"
        elif len(temp_line):
            if temp_line[0] != '#':
                if temp_line[0] == "@":
                    current_section = temp_line[1:].strip()
                    current_section = current_section.lower()
                else:
                    temp_split = temp_line.split(':')
                    if len(temp_split) > 1:
                        setting = temp_split[0].strip()
                        value = ""
                        value = value.join(temp_split[1:])
                        value = value.strip()
                        if len(value) < 1:
                            value = None
                        if current_section == 'header':
                            parsed_data['issue'][setting] = value
                        elif current_section == 'node':
                            parsed_data['node'][setting] = value
                        # If we have something outside of the three
                        # known sections, we kind of have to ignore it
                        # after all, where would it go?
    fd.close()
    return parsed_data

def cli_printnode(fp, issue, node, issue_order, node_order):
    """
    cli_printnode(fp, issue, node, schema_issue, schema_node)
    Given issue and node details, will print
    the current node to the file object fp
    """
    # Start out with the issue metadata
    data = "TICKET NUMBER : %s\n" % issue['short_hash_id']
    for i in issue_order['short']:
        if i != 'short_hash_id':
            if i == 'time':
                data = data + "Time: %s\n" % swarm_time.human_readable_from_stamp(issue['time'])
            else:
                data = data + "%s : %s\n" % (i, issue[i])
    data = data + "\n"
    for i in issue_order['long']:
        data = data + "%s : %s\n" % (i, issue[i])

    data = data + "\n---------------------------\n\n"

    # Now do the node data
    for i in node_order['short']:
        if i == 'time':
            data = data + "Post time: %s\n" % swarm_time.human_readable_from_stamp(node['time'])
        else:
            data = data + "%s : %s\n" % (i, node[i])

    for i in node_order['long']:
        data = data + "\n%s:\n%s\n" % (i, node[i])

    temp = os.write(fp, data)

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

def cli_pager(name):
    """
    Given a filename, view it in some external pager
    """

    # TODO: This needs to be fixed, we ought to try various pagers
    # right now we just kind of assume less is available...
    # which is dumb :-P

    cmd = "less %s" % (name)
    status = os.system(cmd)

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

    master_init(project_name, working_dir, log, force)
    logger.unregister()

def cli_taxonomy(pre_options, pre_args, command, post_options):
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

def cli_log(pre_options, pre_args, command, post_options):
    verbose = 0
    working_dir = os.getcwd()

    for o, a in pre_options:
        if o in ("-v", "--verbose"):
            verbose = verbose + 1

    if post_options:
        working_dir = post_options[0]

    log.set_universal_loglevel(verbose)
    logger.register("cli_log")

    sw = Swarm(working_dir, log)
    xlog = sw.get_transaction_log()
    # FIXME
    # This is ugly, was just an early hack that
    # is still around
    print xlog

    sw.close()
    logger.unregister()

def cli_last(pre_options, pre_args, command, post_options):
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
        logger.enrty("There is no last issue set.", 0)

    sw.close()
    logger.unregister()

def cli_thread(pre_options, pre_args, command, post_options):
    verbose = 0
    working_dir = os.getcwd()
    ticket_number = None
    sw = None

    for o, a in pre_options:
        if o in ("-v", "--verbose"):
            verbose = verbose + 1

    log.set_universal_loglevel(verbose)
    logger.register("cli_last")

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

    if sw:
        if sw.loaded:
            if not ticket_number:
                if sw.config.has_section('cli'):
                    ticket_number = sw.config.get('cli', 'last_issue')

            if ticket_number:
                issue = sw.get_issue(ticket_number)
                schema_issue = sw.get_schema('issue')
                schema_node = sw.get_schema('node')
                if len(issue) == 1:
                    cur_node_id = issue[0]['root_node']
                    node = sw.get_node(cur_node_id)
                    more_nodes = True
                    while more_nodes:
                        if len(node):
                            (fp, name) = tempfile.mkstemp()
                            cli_printnode(fp, issue[0], node[0], sw.get_table_order('issue'), sw.get_table_order('node'))
                            cli_pager(name)
                            os.close(fp)
                            os.remove(name)
                            children = None
                            if node[0]['children']:
                                children = [ x.strip() for x in node[0]['children'].split(',')]
                            else:
                                more_nodes = False
                else:
                    logger.error("The ticket provided seems to have duplicates.\n Sorry, you're on your own until we provide some means to repair conflicts like this.\n Hey, you know, you could help out with swarm and fix this rather serious problem :-)")
            else:
                logger.error("No ticket found.")
        else:
            logger.error("No swarm repository found.")

        sw.close()
    logger.unregister()

def cli_new(pre_options, pre_args, command, post_options):
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
            temp = os.write(fp, "%s:\n" % element)

    temp = os.write(fp, "\n@ NODE\n")
    meta_data = ['related', 'summary']
    for element in meta_data:
        if schema_node.has_key(element):
            temp = os.write(fp, "%s:\n" % element)

    temp = os.write(fp, "\n# Everything after details (including lines begining with '#' or '@') will\n# be considered part of the details section\n@ DETAILS\n\n")

    os.close(fp)

    (bhash, ahash, bsize, asize) = cli_launch_editor(name)
    if bhash != ahash:
        parsed_data = cli_parse_issuefile(name, schema_issue, schema_node)
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
    'log' : Command(
        ['v'],
        ['verbose'],
        'swarm [OPTIONS] log [ISSUE] [DIR]',
        'Displays the log (master log or for a given issue)',
        ['  Will display the log. If [ISSUE] is empty (or 0), will',
         '  display the master log for the DITS repository. If',
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
        cli_thread),
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
