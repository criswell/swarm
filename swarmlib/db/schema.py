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

from sqlalchemy.orm import mapper, relation, backref

from swarmlib.db import metadata

__HASH_ID_LENGTH__ = 40
__USER_ID_LENGTH__ = 60
__SUMMARY_LENGTH__ = 255

issues_table = Table('issues', metadata,
    Column('hash_id', String(40), primary_key=True, unique=True, nullable=False),
    Column('short_hash_id', String(40), unique=True, nullable=False),

    # XXX: The following all need to have default values. The best way
    # will probably be to set up a mapping in sqlalchemy orm, but I don't
    # yet know how best to do this, so I'm marking it as a FIXME
    #Column('component', Integer, nullable=False),
    #Column('version', Integer, nullable=False),
    #Column('milestone', Integer, nullable=False),
    #Column('severity', Integer, nullable=False),
    #Column('priority', Integer, nullable=False),
    #Column('status', Integer, nullable=False),
    #Column('resolution', Integer, nullable=False),

    #Column('owner', String(__USER_ID_LENGTH__)),
    #Column('reporter', String(__USER_ID_LENGTH__), nullable=False),

    # FIXME XXX: More mappings will be needed here
    #Column('cc_id', Integer),
    #Column('subscribers_id', Integer),

    #Column('time', Float),
)

self.nodes_table = Table('nodes', metadata,
    Column('hash_id', String(40), primary_key=True, unique=True, nullable=False),
    Column('summary', String(100), nullable=False),
    Column('issue_id', String(40), ForeignKey('issues.hash_id')),
    Column('parent_node_id', String(40), ForeignKey('nodes.hash_id')),

    #Column('time', Float),

    #Column('poster', String(__USER_ID_LENGTH__)),

    # FIXME XXX: Need to be mapped
    #Column('related_id', Integer),

    #Column('summary', String(__SUMMARY_LENGTH__)),
    #Column('details', Text),

    #Column('attachment_id', String(__HASH_ID_LENGTH__)),
)

class Issue(object):
    def __init__(self, hash_id, short_hash_id):
        self.short_hash_id = short_hash_id
        self.hash_id = hash_id
    def __repr__(self):
       return "<Issue('%s', '%s')>" % (self.hash_id, self.short_hash_id)

class Node(object):
    def __init__(self, hash_id, summary):
        self.hash_id = hash_id
        self.summary = summary
    def __repr__(self):
        return "<Node('%s', '%s')>" % (self.hash_id, self.summary)

mapper(Issue, issues_table, properties={
    'root_nodes':relation(Node) #, backref='issue')
})
mapper(Node, nodes_table, properties={
    'children':relation(Node, backref=backref('parent', remote_side=[nodes_table.c.hash_id]))
})

