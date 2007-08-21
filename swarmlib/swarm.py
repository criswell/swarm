#!/usr/bin/env python

# swarmlib - Main swarmlib module
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

import socket
import os

import swarmlib.config as Config
import swarmlib.data_tools as data_tools
import swarmlib.swarm_time as swarm_time
from swarmlib.db import swarmdb
from swarmlib.db import taxonomy_terms
from swarmlib.db import __MASTER_ISSUE__
from swarmlib.db import table_schema
from swarmlib.db import table_orders

def master_init(project_name, working_dir, log, force=False):
    """
    master_init(working_dir, log, force=False)
    This is called when an issue repository is to be
    initialized for the first time.
    Use force=True to overwrite any existing issue
    repository elements that may be found.
    """
    config = Config.config(working_dir, log, force)
    project_hash = data_tools.get_hash(project_name, swarm_time.human_readable_from_stamp(), socket.getfqdn())
    config.init(project_name, project_hash)
    db = swarmdb(working_dir, config, log, force)
    db.backend.init()
    db.backend.close()

class swarm:
    def __init__(self, working_dir, log, force=False):
        """
        __init__(working_dir, log, force=False)
        Main swarm class interface for all the nastiness
        that goes on behind the scene.
        """
        self._working_dir = working_dir
        self._log = log
        self._force = force
        self._logger = log.get_logger("swarm")
        self.config = None
        self.db = None
        self.loaded = False

        self._setup()

    def _setup(self):
        """
        Internal setup function
        """
        self._logger.register("_setup")

        self.config = Config.config(self._working_dir, self._log)
        self.db = swarmdb(self._working_dir, self.config, self._log)
        if self.db.backend:
            self.loaded = True
            self.db.backend.connect()
        else:
            self._logger.error("Database backend not loaded")

        self._logger.unregister()

    def get_issue(self, ticket_number):
        """
        Given a ticket_number, get the issue
        """

        self._logger.register("get_issue")
        search_criteria = {}

        issue = None
        if ticket_number and self.loaded:
            search_criteria['short_hash_id'] = ticket_number
            self._logger.entry("Fetching for ticket '%s'." % ticket_number, 1)
            issue = self.db.backend.fetch('issue', search_criteria)

        self._logger.unregister()
        return issue

    def get_node(self, node_id):
        """
        Given a node_id, get the issue
        """

        self._logger.register("get_node")
        search_criteria = {}

        node = None
        if node_id and self.loaded:
            search_criteria['node_id'] = node_id
            self._logger.entry("Fetching for node '%s'." % node_id, 1)
            issue = self.db.backend.fetch('node', search_criteria)

        self._logger.unregister()
        return issue

    def get_lineage(self, parent_id=None, child_id=None):
        """
        Given parent or child ids, return the lineage
        """

        self._logger.register("get_lineage")
        lineage = None
        search_criteria = {}

        if not child_id and parent_id:
            search_criteria['parent_id'] = parent_id
            self._logger.entry("Fetching children of parent_id '%s'." % parent_id, 1)
        elif not parent_id and child_id:
            search_criteria['child_id'] = child_id
            self._logger.entry("Fetching parent(s) of child_id '%s'." % child_id, 1)

        if search_criteria: lineage = self.db.backend.fetch('lineage', search_criteria)

        self._logger.unregister()
        return lineage

    def get_taxonomy(self, tax_term):
        """
        Given a table name, will return the list of the
        taxonomy that table describes
        """
        return self.db.backend.get_taxonomy(tax_term)

    def _set_taxonomy(self, term, the_list):
        """
        INTERNAL FUNCTION, DONT CALL
        Given a table name, will update its contents with the new
        terms from 'the_list'
        """
        self.db.backend.set_taxonomy(term, the_list)

    def set_taxonomy(self, term, the_list):
        """
        Given a table name, will update its contents with the new
        terms from 'the_list'
        """
        # TODO, we should probably do some error checking here
        self._set_taxonomy(term, the_list)

    def get_user(self):
        """
        Returns the user information.
        Will search in the following order for it:
        environ variable "SWARMUSER"
        configs (system, user, repo)
        figure it out from os.env and fqdn
        """
        # FIXME!
        # This is a stub
        return '%s@%s' % (os.environ.get('USER'), socket.getfqdn())

    def get_schema(self, name):
        """
        get_schema(name)
        Given a name of a table, get the schema for that table
        """
        schema = {}
        table_in_use = None

        # First, get the schema:
        for table in table_schema:
            if table.name == name:
                table_in_use = table
                break

        if not table_in_use:
            raise swarm_error("No table named '%s'" % name)

        for column in table_in_use.columns:
            schema[column.name] = column.data_type

        return schema

    def get_table_order(self, name):
        """
        get_table_order(name)
        Given a name of a table, get the table print order for that table
        """
        order = None

        if table_orders[name]:
            order = table_orders[name]

        return order

    def get_transaction_log(self, issue=None, lower_entry=None, upper_entry=None, lower_date=None, upper_date=None, xaction=None):
        """
        get_transaction_log(...)
        Get a transaction log slice. Accepts the following parameters:
        issue : If you don't specify an issue, will default to None (e.g., all entries)
        lower_entry : The lower log entry number to start at, will default to None (e.g., no lower limit)
        upper_entry : The upper log entry number to end at, will default to None (e.g., no upper limit)
        lower_date : The lower date to start at, will default to None (e.g., begining of time)
        upper_date : The upper date to end at, will default to None (e.g., the end of days)
        xaction : The transaction to filter by, will default to None

        If called with no parameters will just return the entire transaction log.

        The most common use for this will be to find changes to the repo or to individual
        issues. For example, let's say there's an external repo that is wanting to sync
        with us. The last time they synced was at log entry #871, and they are requesting
        all the changes since then. This function would be called as:
          get_transaction(lower_entry=871)

        easy, no?

        Okay, let's next suppose that we have an external repo that is tracking issue #45
        on our repo. They haven't synced since log entry #4711, so they want all changes
        since then for issue #45 only. The function would be called as:
          get_transaction(issue=45, lower_entry=4711)

        Anyway... there's more you can do with dates and things, but I wont go into that
        here.
        """

        [meta_data] = self.get_issue(issue)

        return self.db.backend.search_transaction_log(meta_data['hash_id'], lower_entry, upper_entry, lower_date, upper_date, xaction)

    def get_last_hash(self, table_name):
        """
        (short_hash, full_hash) = get_last_hash(table_name)
        Given a table name, get the hash for the last ticket added.
        Returns (full_hash, part_hash)
        """
        data = self.db.backend.get_last_record(table_name, 'time')
        if data:
            return (data['hash_id'], data['short_hash_id'])
        else:
            return ("", "")

    def get_unique(self, issue_id):
        """
        hash = get_unique(issue_id)
        Given an issue id, determine a unique "human readable" (e.g., short)
        sub-section hash of it
        """
        length = 4 # The starting, default length of the hash id
        issue_id = issue_id.lower()
        hash_id = issue_id[:length]
        while self.db.backend.fetch('issue', {'short_hash_id': hash_id}):
            length += 1
            if length < len(issue_id):
                hash_id = issue_id[:length]
            else:
                return None

        return hash_id

    def new_issue(self, issue_data):
        """
        new_issue(issue_data)
        """

        # Get a node_id
        # (should we verify this isn't in the db?)
        node_id = data_tools.get_hash(self.config.get('main', 'project_hash'), str(issue_data['issue']['time']), issue_data['issue']['reporter'])

        # Set the root_node to that node_id
        issue_data['issue']['root_node'] = node_id
        issue_data['node']['node_id'] = node_id

        # Set to the default status
        default_status = self.db.backend.get_taxonomy_default('status')
        if default_status:
            issue_data['issue']['status'] = default_status['id']
        else:
            raise swarm_error("Couldn't find the default status. The database may be corrupt.")

        # Generate the next issue hash
        (fh, ph) = self.get_last_hash('issue')
        issue_id = data_tools.get_hash(fh, ph, str(issue_data['issue']['time']))
        (issue_data['issue']['hash_id'], issue_data['issue']['short_hash_id']) = (issue_id, self.get_unique(issue_id))

        # Add the issue, obtaining the issue id
        self.db.backend.new_issue(issue_data['issue'])
        # Add the new node
        #issue_data['node']['root'] = issue_rowid
        self.db.backend.new_node(issue_data['node'], issue_data['issue']['hash_id'])
        # Add issue_to_node
        issue_to_node = {'issue_id': issue_id, 'node_id': node_id}
        self.db.backend.link_issue_to_node(issue_to_node)

        return issue_data['issue']['short_hash_id']

    def update_issue(self, issue_data):
        """
        Given new issue data, will update the issue (header)
        """
        self._logger.register('update_issue')
        if issue_data.has_key("hash_id") and issue_data.has_key("short_hash_id"):
            self._logger.entry("Updating issue #%s" % issue_data['short_hash_id'], 1)
            self._logger.entry("- Long hash_id '%s'" % issue_data['hash_id'], 3)
            self.db.backend.update_issue(issue_data)

        self._logger.unregister()

    def add_node(self, issue_data, parent_node):
        """
        add_node(issue_data)
        Add a new node to the DB
        """

        self._logger.register('add_node')

        node_id = data_tools.get_hash(issue_data['issue']['hash_id'], str(issue_data['node']['time']), issue_data['node']['poster'])
        issue_data['node']['node_id'] = node_id
        self.db.backend.new_node(issue_data['node'], issue_data['issue']['hash_id'])
        # Add issue_to_node
        issue_to_node = {'issue_id': issue_data['issue']['hash_id'], 'node_id': node_id}
        self.db.backend.link_issue_to_node(issue_to_node)
        # Update lineage
        node_lineage = {'parent_id': parent_node['node_id'] , 'child_id': node_id}
        self.db.backend.add_lineage(node_lineage, issue_data['issue']['hash_id'])

        self._logger.unregister()

    def close(self):
        """
        Closes the database (syncronizing data) as well as all
        open xlog files.
        """
        if self.loaded:
            self.db.backend.close()
