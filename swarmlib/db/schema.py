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
                       Float, PickleType, Text, Binary, Boolean

from sqlalchemy.orm import mapper, relation, backref
import sqlalchemy.types as types

from swarmlib.db.db_bits import metadata

###################################
# Define the issue and node tables
###################################

__HASH_ID_LENGTH__ = 40
__USER_ID_LENGTH__ = 60
__SUMMARY_LENGTH__ = 255

issues_table = Table('issues', metadata,
    Column('hash_id', String(__HASH_ID_LENGTH__),
            primary_key=True, unique=True, nullable=False),
    Column('short_hash_id', String(__HASH_ID_LENGTH__),
            unique=True, nullable=False),

    Column('block_id', String(__HASH_ID_LENGTH__),
            ForeignKey('issues.hash_id')),

    # Status will no longer be a user definable list
    # This is to better refine searches.
    Column('status', Integer, nullable=False),

    # XXX: The following all need to have default values. The best way
    # will probably be to set up a mapping in sqlalchemy orm, but I don't
    # yet know how best to do this, so I'm marking it as a FIXME
    Column('component', Integer, nullable=False),
    Column('version', Integer, nullable=False),
    Column('milestone', Integer, nullable=False),
    Column('severity', Integer, nullable=False),
    Column('priority', Integer, nullable=False),
    Column('resolution', Integer, nullable=False),

    Column('owner', String(__USER_ID_LENGTH__)),
    Column('reporter', String(__USER_ID_LENGTH__), nullable=False),

    # FIXME XXX: More mappings will be needed here
    Column('cc_id', Integer),
    Column('subscribers_id', Integer),

    Column('time', Float),
)

nodes_table = Table('nodes', metadata,
    Column('hash_id', String(__HASH_ID_LENGTH__),
            primary_key=True, unique=True, nullable=False),
    Column('summary', String(__SUMMARY_LENGTH__), nullable=False),
    Column('issue_id', String(__HASH_ID_LENGTH__),
            ForeignKey('issues.hash_id')),
    Column('parent_node_id', String(__HASH_ID_LENGTH__),
            ForeignKey('nodes.hash_id')),

    Column('time', Float),

    Column('poster', String(__USER_ID_LENGTH__)),

    Column('summary', String(__SUMMARY_LENGTH__)),
    Column('details', Text),

    Column('attachment', Binary),
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
    'root_nodes':relation(Node), #, backref='issue')
    'depends':relation(Issue, backref=backref('blocks',
            remote_side=[issues_table.c.hash_id])),
})
mapper(Node, nodes_table, properties={
    'children':relation(Node, backref=backref('parent',
            remote_side=[nodes_table.c.hash_id])),
})

###################################
# Define the Transaction log table
###################################

transaction_log_table = Table('transaction_log', metadata,
    Column('id', Integer,  primary_key=True, auto_increment=True),
    Column('root', String(__HASH_ID_LENGTH__)),
    Column('time', Float),
    Column('transaction', Integer),
    Column('transaction_data', PickleType),
)

class TransactionEntry(object):
    def __init__(self, root, time, transaction, transaction_data):
        self.root = root
        self.time = time
        self.transaction = transaction
        self.transaction_log = transaction_log

    def __repr__(self):
        return "<TransactionEntry(root:'%s', time:'%s'>" % (self.root,
                self.time)

mapper(TransactionEntry, transaction_log_table)

############################################
# Define the user-definable Taxonomy tables
############################################
__TAX_NAME_LENGTH__ = 25
##################
component_table = Table('components', metadata
    Column('id', Integer, primary_key=True, unique=True, auto_increment=True),
    Column('name', String(__TAX_NAME_LENGTH__)),
    Column('isdefault', Boolean),
)

class ComponentEntry(object):
    def __init__(self, name, isdefault=False):
        self.name = name
        self.isdefault = isdefault

    def __repr__(self):
        return "<ComponentEntry('%s', default:'%s')>" % (self.name,
                self.isdefault)

mapper(ComponentEntry, component_table)
##################
version_table = Table('versions', metadata
        column('id',Integer, primary_key=True, unique=True,
                auto_increment=True),
        column('name', String(__TAX_NAME_LENGTH__)),
        column('isdefault', Boolean),
)

class VersionEntry(object):
    def __init__(self, name, isdefault=False):
        self.name = name
        self.isdefault = isdefault

    def __repr__(self):
        return "<VersionEntry('%s', default:'%s')>" % (self.name,
                self.isdefault)

mapper(VersionEntry, version_table)
##################
milestone_table = Table('milestones', metadata
        column('id',Integer, primary_key=True, unique=True,
                auto_increment=True),
        column('name', String(__TAX_NAME_LENGTH__)),
        column('isdefault', Boolean),
)

class MilestoneEntry(object):
    def __init__(self, name, isdefault=False):
        self.name = name
        self.isdefault = isdefault

    def __repr__(self):
        return "<MilestoneEntry('%s', default:'%s')>" % (self.name,
                self.isdefault)

mapper(MilestoneEntry, milestone_table)
##################
severity_table = Table('severities', metadata
        column('id',Integer, primary_key=True, unique=True,
                auto_increment=True),
        column('name', String(__TAX_NAME_LENGTH__)),
        column('isdefault', Boolean),
)

class SeverityEntry(object):
    def __init__(self, name, isdefault=False):
        self.name = name
        self.isdefault = isdefault

    def __repr__(self):
        return "<SeverityEntry('%s', default:'%s')>" % (self.name,
                self.isdefault)

mapper(SeverityEntry, severity_table)
##################
priority_table = Table('priorities', metadata
        column('id',Integer, primary_key=True, unique=True,
                auto_increment=True),
        column('name', String(__TAX_NAME_LENGTH__)),
        column('isdefault', Boolean),
)

class PriorityEntry(object):
    def __init__(self, name, isdefault=False):
        self.name = name
        self.isdefault = isdefault

    def __repr__(self):
        return "<PriorityEntry('%s', default:'%s')>" % (self.name,
                self.isdefault)

mapper(PriorityEntry, priority_table)
##################
status_table = Table('status', metadata
        column('id',Integer, primary_key=True, unique=True,
                auto_increment=True),
        column('name', String(__TAX_NAME_LENGTH__)),
        column('isdefault', Boolean),
)

class StatusEntry(object):
    def __init__(self, name, isdefault=False):
        self.name = name
        self.isdefault = isdefault

    def __repr__(self):
        return "<StatusEntry('%s', default:'%s')>" % (self.name,
                self.isdefault)

mapper(StatusEntry, status_table)
##################
resolution_table = Table('resolutions', metadata
        column('id',Integer, primary_key=True, unique=True,
                auto_increment=True),
        column('name', String(__TAX_NAME_LENGTH__)),
        column('isdefault', Boolean),
)

class ResolutionEntry(object):
    def __init__(self, name, isdefault=False):
        self.name = name
        self.isdefault = isdefault

    def __repr__(self):
        return "<ResolutionEntry('%s', default:'%s')>" % (self.name,
                self.isdefault)

mapper(ResolutionEntry, resolution_table)
##################
