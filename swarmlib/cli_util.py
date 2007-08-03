#!/usr/bin/env python

# cli_util - Various CLI utilities
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

import os
import swarmlib.swarm_time as swarm_time

class util:
    def __init__(self, sw, log):
        self.sw = sw
        self.log = log
        self.logger = self.log.get_logger("cli_util.util")

    def space_filler(self, text, size):
        """
        space_filler(self, text, size)
        Given text and a requested size, return empty space that,
        when added to text, will fill up to size.
        """
        a = " "
        if size > len(text):
            a = " " * (size - len(text))
        return a

    def parse_datafile(self, name, column_list):
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
                        self.logger.error("Unable to parse line, skipping: '%s'" % temp_line)

        fd.close()
        return parsed_list

    def parse_issuefile(self, name, schema_issue, schema_node):
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
                                if schema_issue[setting].lower() == "integer" and value:
                                    parsed_data['issue'][setting] = int(value)
                                elif schema_issue[setting].lower() == "float" and value:
                                    parsed_data['issue'][setting] = float(value)
                                else:
                                    parsed_data['issue'][setting] = value
                            elif current_section == 'node':
                                if schema_node[setting].lower() == "integer" and value:
                                    parsed_data['node'][setting] = int(value)
                                elif schema_node[setting].lower() == "float" and value:
                                    parsed_data['node'][setting] = float(value)
                                else:
                                    parsed_data['node'][setting] = value
                            # If we have something outside of the three
                            # known sections, we kind of have to ignore it
                            # after all, where would it go?
        fd.close()
        return parsed_data

    def print_node(self, fp, issue, node, issue_order, node_order):
        """
        print_node(fp, issue, node, schema_issue, schema_node)
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

    def launch_editor(self, name):
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

    def pager(self, name):
        """
        Given a filename, view it in some external pager
        """

        # TODO: This needs to be fixed, we ought to try various pagers
        # right now we just kind of assume less is available...
        # which is dumb :-P

        cmd = "less %s" % (name)
        status = os.system(cmd)
