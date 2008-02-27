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

# FIXME
# Should do some tests here, import pickle if cPickle doesn't work
import cPickle as pickle
import binascii

import swarmlib.data_tools as data_tools

class Xaction:
    def __init__(self, description, encoder_callback, decoder_callback, hr_callback):
        self.description = description
        self.encode = encoder_callback
        self.decode = decoder_callback
        self.decode_human_readable = hr_callback

class xaction_dispatch:
    def __init__(self):
        self.sw = None
        self.dispatch = {
            'xlog_start' : Xaction(
                'Transaction log start',
                self.null_callback,
                self.null_callback,
                self.hr_xlog_start),
            'set_taxonomy' : Xaction(
                'Set taxonomy terms',
                self.enc_simple_obj,
                self.dec_simple_obj,
                self.hr_set_taxonomy),
            'link_issue_to_node' : Xaction(
                'Link an issue to a node',
                self.enc_simple_obj,
                self.dec_simple_obj,
                self.hr_link_issue_to_node),
            'add_lineage' : Xaction(
                'Link parent and children in lineage',
                self.enc_simple_obj,
                self.dec_simple_obj,
                self.hr_add_lineage),
            'new_node' : Xaction(
                'Create a new node',
                self.enc_node_id,
                self.dec_node_id,
                self.hr_new_node),
            'new_issue' : Xaction(
                'Create a new issue',
                self.enc_hash_id,
                self.dec_hash_id,
                self.hr_issue_data),
            'update_issue' : Xaction(
                'Update an issue',
                self.enc_hash_id,
                self.dec_hash_id,
                self.hr_issue_data),
            'add_tracker' : Xaction(
                'Add an upstream tracker',
                self.null_callback,
                self.null_callback,
                self.hr_tracker),
        }

    def set_swarm(self, sw):
        """
        Call this to set the Swarm instance. If this isn't called, some functionality will be lost.
        """
        self.sw = sw

    # The following should only be accessed through the dispatch!
    def null_callback(self, xdata=None):
        """
        This is the null_callback. It returns what you pass it exactly,
        and defaults to None.
        """
        return xdata

    def enc_simple_obj(self, xdata):
        return binascii.hexlify(pickle.dumps(xdata))

    def dec_simple_obj(self, xdata):
        return pickle.loads(binascii.unhexlify(xdata))

    def enc_node_id(self, xdata):
        return xdata['node_id']

    def dec_node_id(self, xdata):
        rdata = {}
        rdata['node_id'] = xdata
        return rdata

    def enc_hash_id(self, xdata):
        return xdata['hash_id']

    def dec_hash_id(self, xdata):
        rdata = {}
        rdata['hash_id'] = xdata
        return rdata

    # The following are the human readable (hr) functions
    # They should return human readable text (someday,
    # localization would be lovely) describing what happened
    # This isn't intended to be parsable by machines, it's
    # just something to help humans understand what happened.
    # So really, the format could change at any time.

    def hr_xlog_start(self, root, xdata):
        return "Swarm hive was created and transaction log started."

    def hr_set_taxonomy(self, root, xdata):
        tax_list = self.dispatch['set_taxonomy'].decode(xdata)
        message = ""
        for key in tax_list.keys():
            message = message + "Taxonomy for term '%s' updated to the following:\n\t%s" % (key, tax_list[key])
        return message

    def hr_link_issue_to_node(self, root, xdata):
        data = self.dispatch['link_issue_to_node'].decode(xdata)
        [issue] = self.sw.get_issue(None, data['issue_id'])
        [node] = self.sw.get_node(data['node_id'])
        message = "Node with subject '%s' by '%s' was linked to issue with id '%s'." % (node['summary'], node['poster'], issue['short_hash_id'])
        return message

    def hr_add_lineage(self, root, xdata):
        data = self.dispatch['add_lineage'].decode(xdata)
        return "Link child node '%s' with parent node '%s'." % (data['child_id'], data['parent_id'])

    def hr_new_node(self, root, xdata):
        [issue] = self.sw.get_issue(None, root)
        [node] = self.sw.get_node(xdata)
        message = "Node with subject '%s' by '%s' was created for issue id '%s'." % (node['summary'], node['poster'], issue['short_hash_id'])
        return message

    def hr_issue_data(self, root, xdata):
        data = self.dec_hash_id(xdata)
        [issue] = self.sw.get_issue(None, data['hash_id'])
        message = "Issue id '%s' created or changed." % issue['short_hash_id']
        return message

    def hr_tracker(self, root, xdata):
        data = self.null_callback(xdata)
        # FIXME
        # This needs to be better fleshed out
        message = "Add upstream tracker."
        return message
