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

#
# Database schema
#

class column:
    def __init__(self, name, auto_increment=False, primary_key=False, data_type='text', unique=False):
        self.name = name
        self.auto_increment = auto_increment
        self.primary_key = primary_key
        self.data_type = data_type
        self.unique = unique

class table:
    def __init__(self, name):
        self.name = name
        self.columns = []
    def __getitem__(self, objects):
        self.columns = [ob for ob in objects if isinstance(ob, column)]
        return self

table_schema = [
    # Issue tracking blob
    table('issue')[
        column('id', unique=True),

        column('component'),
        column('version'),
        column('milestone'),

        column('severity'),
        column('priority'),

        column('owner'),
        column('reporter'),
        column('cc'),
        column('subscribers'),

        column('summary'),
        column('details'),
        column('keywords'),

        column('status'),
        column('resolution'),

        column('time', type='int'),
        column('root'),
        ],

    table('issue_custom')[
        column('id'),
        column('name'),
        column('value'),
    ],

    # Issue relation blobs
    table('parents')[
        column('id'),
        column('pid'),
        ],

    table('children')[
        column('id'),
        column('cid'),
        ],

    table('related')[
        column('id'),
        column('rid'),
        ],

    #upstream tracker
    table('upstream')[
        column('id'),
        column('uri'),
        column('type'),
        column('authentication'), # blob containing auth info
        column('transport'), # blob containing transport info
        ],

     ]

class swarmdb:
    def __init__(self, config):