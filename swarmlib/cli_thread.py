#!/usr/bin/env python

# cli_thread - CLI thread command
#
# Copyright 2007 Sam Hart
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Author: Sam Hart

import tempfile
import os
import swarmlib.swarm_time as swarm_time


class thread:
    def __init__(self, sw, log, util, ticket_number):
        self.sw = sw
        self.util = util
        self.ticket_number = ticket_number
        self.log = log
        self.logger = self.log.get_logger("cli_thread")
        [self.issue] = self.sw.get_issue(self.ticket_number)
        self.node = None
        self.schema_issue = self.sw.get_schema('issue')
        self.schema_node = self.sw.get_schema('node')

    def page_node(self):
        """
        Page the current node
        """
        node = self.node[0]
        (fp, name) = tempfile.mkstemp()
        self.util.print_node(fp, self.issue, node, self.sw.get_table_order('issue'), self.sw.get_table_order('node'))
        self.util.pager(name)
        os.close(fp)
        os.remove(name)

    def run(self):
        self.logger.register('run')
        #[issue] = self.sw.get_issue(self.ticket_number)
        #schema_issue = self.sw.get_schema('issue')
        #schema_node = self.sw.get_schema('node')
        if len(self.issue):
            cur_node_id = self.issue['root_node']
            self.node = self.sw.get_node(cur_node_id)
            more_nodes = True
            while more_nodes:
                if len(self.node):
                    self.page_node()
                    children = self.sw.get_lineage(parent_id=cur_node_id)
                    parents = self.sw.get_lineage(child_id=cur_node_id)
                    if parents : print "Parents\n" + str(parents) + "\n"
                    print
                    if children: print "Children\n" + str(children) + "\n"
                    parent_entry = {}
                    child_entry = {}
                    parent_keys = None
                    child_keys = None
                    if parents:
                        for p in parents:
                            [temp_node] = self.sw.get_node(p['parent_id'])
                            parent_entry[temp_node['time']] = [temp_node['poster'], temp_node['summary'], temp_node['node_id']]
                    if children:
                        for c in children:
                            [temp_node] = self.sw.get_node(c['child_id'])
                            child_entry[temp_node['time']] = [temp_node['poster'], temp_node['summary'], temp_node['node_id']]

                    output_text = ""

                    if parent_entry:
                        parent_keys = parent_entry.keys()
                        parent_keys.sort()
                        output_text = output_text + "Parent nodes:\n"
                        for i in range(len(parent_keys)):
                            output_text = output_text + "\t[P%i] '%s' by '%s'\n" % (i, parent_entry[parent_keys[i]][1], parent_entry[parent_keys[i]][0])
                        output_text = output_text + "\n"
                    if child_entry:
                        child_keys = child_entry.keys()
                        child_keys.sort()
                        output_text = output_text + "Child nodes:\n"
                        for i in range(len(child_keys)):
                            output_text = output_text + "\t[C%i] '%s' by '%s'\n" % (i, child_entry[child_keys[i]][1], child_entry[child_keys[i]][0])
                        output_text = output_text + "\n"

                    if child_entry or parent_entry:
                        output_text = output_text + "Select a node to navigate to or"
                    else:
                        output_text = output_text + "Press"
                        more_nodes = False

                    output_text = output_text + "\n\t[R] Reply to the node just viewed\n\t[B] View the previous node again\n\t[Q] Quit viewing the thread\n? "

                    valid_choice = False
                    while not valid_choice:
                        choice = raw_input(output_text)
                        choice = choice.lower()
                        if choice[0] == 'p':
                            # User requested a parent_id
                            if choice[1:].isdigit():
                                num = int(choice[1:])
                                if num in range(len(parent_keys)):
                                    node = self.sw.get_node(parent_entry[num][2])
                                    more_nodes = True
                                    valid_choice = True
                                else:
                                    print "\n'%i' is not a valid parent node!\n" % num
                                    valid_choice = False
                            else:
                                valid_choice = False
                        elif choice[0] == 'c':
                            # user requested a child_id
                            if choice[1:].isdigit():
                                num = int(choice[1:])
                                if num in range(len(child_keys)):
                                    #print child_entry
                                    self.node = self.sw.get_node(child_entry[child_keys[num]][2])
                                    more_nodes = True
                                    valid_choice = True
                                else:
                                    print "\n'%i' is not a valid child node!\n" % num
                                    valid_choice = False
                            else:
                                valid_choice = False
                        elif choice == 'b':
                            valid_choice = True
                            more_nodes = True
                        elif choice == 'q':
                            valid_choice = True
                            more_nodes = False
                        elif choice == 'r':
                            valid_choice = True
                            self.new_comment()
                            more_nodes = True
                        else:
                            valid_choice = False
                            print "\n'%s' choice is not a valid option\n" % choice
        else:
            self.logger.error("Something wrong with the ticket.")

        self.logger.unregister()

    def new_comment(self):
        node = self.node[0]
        self.logger.register('new_comment')
        self.logger.entry("Comment on node '%s'" % node['node_id'], 2)

        (fp, name) = tempfile.mkstemp()
        timestamp = swarm_time.timestamp()
        reporter = self.sw.get_user()
        temp = os.write(fp,
            "# Adding new comment to ticket\n" +
            "#--------------------\n" +
            "# Lines begining with a '#' will be treated as a comment.\n" +
            "# In the header section, blank lines will be ignored\n" +
            "# Lines starting with '@' indicate a section divider.\n\n" +
            "@ HEADER\n\n")
        if self.schema_issue.has_key('time'):
            temp = os.write(fp, "# timestamp: %s\n" % timestamp)
            temp = os.write(fp, "# %s\n" % swarm_time.human_readable_from_stamp(timestamp))
        if self.schema_issue.has_key('reporter'):
            temp = os.write(fp, "# poster: %s\n" % reporter)

        meta_data = ['component', 'version', 'milestone', 'severity', 'priority', 'owner', 'keywords', 'status']
        for element in meta_data:
            if self.schema_issue.has_key(element):
                if self.issue[element]:
                    temp = os.write(fp, "%s:%s\n" % (element, self.issue[element]))
                else:
                    temp = os.write(fp, "%s:\n" % element)

        temp = os.write(fp, "\n@ NODE\n")
        meta_data = ['related', 'summary']
        for element in meta_data:
            if self.schema_node.has_key(element):
                if node[element]:
                    temp = os.write(fp, "%s:%s\n" % (element, node[element]))
                else:
                    temp = os.write(fp, "%s:\n" % element)

        temp = os.write(fp, "\n# Everything after details (including lines begining with '#' or '@') will\n# be considered part of the details section\n@ DETAILS\n\n")

        os.close(fp)

        (bhash, ahash, bsize, asize) = self.util.launch_editor(name)
        if bhash != ahash:
            parsed_data = self.util.parse_issuefile(name, self.schema_issue, self.schema_node)
            parsed_data['node']['time'] = timestamp
            parsed_data['node']['poster'] = reporter
            # Ensure specific items are kept in sync
            parsed_data['issue']['root_node'] = self.issue['root_node']
            parsed_data['issue']['reporter'] = self.issue['reporter']
            parsed_data['issue']['short_hash_id'] = self.issue['short_hash_id']
            parsed_data['issue']['time'] = self.issue['time']
            parsed_data['issue']['hash_id'] = self.issue['hash_id']
            parsed_data['issue']['id'] = self.issue['id']
            #print len(parsed_data['node']['details'].strip())
            print parsed_data['node']
            #print
            #print parsed_data['issue']
            #print
            #print issue
            #print
            if parsed_data['issue'] != self.issue:
                self.sw.update_issue(parsed_data['issue'])

            self.sw.add_node(parsed_data, self.node)
    #        new_id = sw.new_issue(parsed_data)
    #        logger.entry("Ticket #%s has been created." % str(new_id), 0)
    #        if not sw.config.has_section('cli'):
    #            sw.config.add_section('cli')
    #        sw.config.set('cli', 'last_issue', new_id)
    #        sw.config.save()
            self.issue = parsed_data['issue']
            self.node[0] = parsed_data['node']
        else:
            self.logger.entry("Ticket reply cancelled.", 0)

        os.remove(name)

        self.logger.unregister()
        #return (issue, node)

def run(sw, log, util, ticket_number):
    """
    sw = swarm instance
    log = log instance
    util = cli_util instance
    ticket_number = ticket_number(duh)
    """
    t = thread(sw, log, util, ticket_number)
    t.run()
