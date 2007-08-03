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

class thread:
    def __init__(self, sw, log, ticket_number):
        self.sw = sw
        self.ticket_number = ticket_number
        self.log = log
        self.logger = self.log.get_logger("cli_thread")

                [issue] = sw.get_issue(ticket_number)
                schema_issue = sw.get_schema('issue')
                schema_node = sw.get_schema('node')
                if len(issue):
                    cur_node_id = issue['root_node']
                    node = sw.get_node(cur_node_id)
                    more_nodes = True
                    while more_nodes:
                        if len(node):
                            (fp, name) = tempfile.mkstemp()
                            cli_printnode(fp, issue, node[0], sw.get_table_order('issue'), sw.get_table_order('node'))
                            cli_pager(name)
                            os.close(fp)
                            os.remove(name)
                            children = sw.get_lineage(parent_id=cur_node_id)
                            parents = sw.get_lineage(child_id=cur_node_id)
                            print parents
                            print
                            print children
                            parent_entry = {}
                            child_entry = {}
                            parent_keys = None
                            child_keys = None
                            if parents:
                                for p in parents:
                                    [temp_node] = sw.get_node(p['parent_id'])
                                    parent_entry[temp_node['time']] = [temp_node['poster'], temp_node['summary'], temp_node['node_id']]
                            if children:
                                for c in children:
                                    [temp_node] = sw.get_node(c['child_id'])
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
                                            node = sw.get_node(parent_entry[num][2])
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
                                            node = sw.get_node(child_entry[child_keys[num]][2])
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
                                    (issue, node[0]) = cli_new_comment(sw, issue, node[0])
                                    more_nodes = True
                                else:
                                    valid_choice = False
                                    print "\n'%s' choice is not a valid option\n" % choice
                else:
                    logger.error("Something wrong with the ticket.")
