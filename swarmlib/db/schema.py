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

"""
Swarm DB Schema Package

This package defines the database schema used in a Swarm Hive.
"""

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, \
                       Float, PickleType, Text

metadata = MetaData()

__HASH_ID_LENGTH__ = 40
__USER_ID_LENGTH__ = 60

issue_table = Table('issue', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('short_hash_id',  String(__HASH_ID_LENGTH__), unique=True),
    Column('hash_id', String(__HASH_ID_LENGTH__), unique=True),

    # XXX: The following all need to have default values. The best way
    # will probably be to set up a mapping in sqlalchemy orm, but I don't
    # yet know how best to do this, so I'm marking it as a FIXME
    Column('component', Integer, nullable=False),
    Column('version', Integer, nullable=False),
    Column('milestone', Integer, nullable=False),
    Column('severity', Integer, nullable=False),
    Column('priority', Integer, nullable=False),
    Column('status', Integer, nullable=False),
    Column('resolution', Integer, nullable=False),

    Column('owner', String(__USER_ID_LENGTH__)),
    Column('reporter', String(__USER_ID_LENGTH__), nullable=False),

    # FIXME XXX: More mappings will be needed here
    Column('cc_id', Integer),
    Column('subscribers_id', Integer),

    Column('time', Float),

    Column('root_node_id', String(__HASH_ID_LENGTH__),
            ForeignKey('node.node_id')),
)

node_table = Table('node', metadata,
    Column('node_id', String(__HASH_ID_LENGTH__), unique=True),

    Column('time', Float),

    Column('poster', String(__USER_ID_LENGTH__)),

    # FIXME XXX: Need to be mapped
    Column('related_id', Integer),

    Column('summary', Text),
    Column('details', Text),

    Column('attachment_id', String(__HASH_ID_LENGTH__)),

    Column('root_issue_id', String(__HASH_ID_LENGTH__),
            ForeignKey('issue.hash_id')),
)

lineage_table = Table('lineage', metadata,
    Column('parent_id', String(__HASH_ID_LENGTH__),
            ForeignKey('node.node_id')),
    Column('child_id', String(__HASH_ID_LENGTH__),
            ForeignKey('node.node_id')),
)
