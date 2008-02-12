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
    def __init__(self, description, encoder_callback, decoder_callback):
        self.description = description
        self.encode = encoder_callback
        self.decode = decoder_callback

class xaction_dispatch:
    def __init__(self):
        self.dispatch = {
            'xlog_start' : Xaction(
                'Transaction log start',
                self.null_callback,
                self.null_callback),
            'set_taxonomy' : Xaction(
                'Set taxonomy terms',
                self.enc_simple_obj,
                self.dec_simple_obj),
            'link_issue_to_node' : Xaction(
                'Link an issue to a node',
                self.enc_simple_obj,
                self.dec_simple_obj),
            'add_lineage' : Xaction(
                'Link parent and children in lineage',
                self.enc_simple_obj,
                self.dec_simple_obj),
            'new_node' : Xaction(
                'Create a new node',
                self.enc_node_id,
                self.dec_node_id),
            'new_issue' : Xaction(
                'Create a new issue',
                self.enc_hash_id,
                self.dec_hash_id),
            'update_issue' : Xaction(
                'Update an issue',
                self.enc_hash_id,
                self.dec_hash_id),
        }

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
        return binascii.unhexlify(pickle.loads(xdata))

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

