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

# This encodes and decodes the tracker information

import os.path
import swarmlib.data_tools as data_tools

class Tracker:
    def __init__(self, description, encoder_callback, decoder_callback):
        self.description = description
        self.encoder = encoder_callback
        self.decoder = decoder_callback

class tracker_dispatch:
    def __init__(self, hive=None):
        self.hive = hive
        self.dispatch = {
            'swarm_local' : Tracker(
                'A locally mounted filesystem',
                self.encode_local,
                self.decode_local
            ),
        }

    def encode(self, transport):
        """
        stub
        """
        if self.hive:
            return self.dispatch[self.hive.scheme].encoder(transport)
        else:
            return None

    def decode(self):
        """
        stub
        """
        if self.hive:
            return self.dispatch[self.hive.scheme].decoder()
        else:
            return None

    # The following should only be accessed through the dispatch!
    def encode_local(self, transport):
        """
        Returns a pythonic dictionary ready for insertion into the upstream
        tracker db
        """
        upstream = None

        if self.hive:
            uri = os.path.abspath(self.hive.path)
            tracker_id = data_tools.get_hash(uri, transport, self.hive.scheme)
            upstream = {
                'tracker_id' : tracker_id,
                'uri' :  uri,
                'type' : 'swarm_local',
                'authentication' : None,
                'transport' : transport
            }

        return upstream

    def decode_local(self):
        """
        stub
        """

        return None

tracker = tracker_dispatch()
