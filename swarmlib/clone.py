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

class clone:
    def __init__(self, source_sw, dest_sw, log):
        """
        source_sw == The source Swarm instance
        dest_sw == The destination Swarm instance
        log == The log instance
        """
        self._source_sw = source_sw
        self._dest_sw = dest_sw
        self._log = log
        self._logger = log.get_logger("clone")
        self._callback = {
            'xlog_start' : self.clone_xlog_start,
            'set_taxonomy' : self.clone_set_taxonomy,
            'link_issue_to_node' : self.clone_link_issue_to_node,
            'add_lineage' : self.clone_add_lineage,
            'new_node' : self.clone_new_node,
            'new_issue' : self.clone_new_issue,
            'update_issue' :self.clone_update_issue,
        }

    def run(self):
        """
        Run the clone transaction
        """

        self._logger.register("run")

        # First, set the project_name
        # Note that this is the *only* item we currently clone from the
        # source configuration file. If anyone can come up with any
        # compelling reasons to include anything else, I'll happily add
        # them.
        self._dest_sw.config.set('main', 'project_name', self._source_sw.config.get('main', 'project_name', 'swarm'))
        self._dest_sw.config.save()

        # Next, get the transaction log from the source_sw
        # FIXME: This isn't very scalable, we probably should
        # do this in clumps of xaction log entries
        xlog = self._source_sw.get_transaction_log()
        self._logger.entry("Processing '%i' transactions" % len(xlog), 0)

        # Now, run through each xaction, and replay it
        # into the dest_sw
        errors = 0
        for (xid, root, time, xaction, xdata) in xlog:
            if not self._callback[xaction](xid, root, time, xaction, xdata):
                errors = errors

        if errors > 0:
            self._logger.error("There were '%i' errors in the clone transaction" % errors)
        else:
            self._logger.entry("No errors in the clone transaction", 0)

        self._logger.unregister()

    # The clone transactions
    # These should not be called outside of the callback
    # dictionary

    def clone_xlog_start(self, xid, root, time, xaction, xdata):
        """
        xlog_start transaction
        root == __MASTER_ISSUE__
        xaction = 'xlog_start'
        xdata = Nothing
        """
        self._logger.register('xlog_start')
        self._logger.entry('Cloning %s transaction' % xaction, 1)

        self._dest_sw.db.backend.log_transaction(root, xaction, xdata, xid, time, True)

        self._logger.unregister()

    def clone_set_taxonomy(self, xid, root, time, xaction, xdata):
        """
        set_taxonomy transaction
        root = __MASTER_ISSUE__
        xaction = 'set_taxonomy'
        """
        self._logger.register('set_taxonomy')
        self._logger.entry('Cloning %s transaction' % xaction, 1)
        data = self._dest_sw.xactions.dispatch[xaction].decode(xdata)
        [term] = data.keys()
        the_list = data[term]

        self._dest_sw.set_taxonomy(term, the_list)

        self._logger.unregister()

    def clone_add_lineage(self, xid, root, time, xaction, xdata):
        """
        add_lineage transaction
        root = root issue id
        xdata = {'parent_id': parent_node_id , 'child_id': child_node_id}
        """
        self._logger.register('clone_add_lineage')
        self._logger.entry('Cloning %s transaction' % xaction, 1)

        data = self._dest_sw.xactions.dispatch[xaction].decode(xdata)

        self._dest_sw.db.backend.add_lineage(data, root, time)

        self._logger.unregister()

    def clone_new_node(self, xid, root, time, xaction, xdata):
        """
        new_node transaction
        root = root issue id
        xdata = data['node_id'] = node_id
        """
        self._logger.register('clone_new_node')
        self._logger.entry('Cloning %s transaction' % xaction, 1)

        # Technically, this is just stored as node_id, however
        # since we reserve the right to change the transaction
        # log schema at any time the safest way to get this is
        # to use the dispatch.decode function.
        node_id = self._source_sw.xactions.dispatch[xaction].decode(xdata)['node_id']

        node_data = self._source_sw.get_node(node_id)
        # ERE I AM JH
        print node_data

        self._logger.unregister()

    def clone_new_issue(self, xid, root, time, xaction, xdata):
        """
        new_issue transaction
        root = __MASTER_ISSUE__
        xdata = data['hash_id'] = hash_id
        """

        self._logger.register('clone_new_issue')
        self._logger.entry('Cloning %s transaction' % xaction, 1)

        hash_id = self._source_sw.xactions.dispatch[xaction].decode(xdata)['hash_id']

        issue_data = self._source_sw.get_issue(None, hash_id)
        # ERE I AM JH
        print issue_data

        self._logger.unregister()

    def clone_link_issue_to_node(self, xid, root, time, xaction, xdata):
        """
        stub
        """

        self._logger.register('clone_link_issue_to_node')
        self._logger.entry('Cloning %s transaction' % xaction, 1)

        self._logger.unregister()

    def clone_update_issue(self, xid, root, time, xaction, xdata):
        """
        stub
        """

        self._logger.register('clone_update_issue')
        self._logger.entry('Cloning %s transaction' % xaction, 1)

        self._logger.unregister()
