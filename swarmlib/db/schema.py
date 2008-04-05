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

#from sqlalchemy.orm import mapper, relation, backref
#import sqlalchemy.types as types

from swarmlib.db.db_bits import metadata
import swarmlib.db.data_objects as dobj

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

mapper(dobj.Issue, issues_table, properties={
    'root_nodes':relation(Node), #, backref='issue')
    'depends':relation(Issue, backref=backref('blocks',
            remote_side=[issues_table.c.hash_id])),
})
mapper(dobj.Node, nodes_table, properties={
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

mapper(dobj.TransactionEntry, transaction_log_table)

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

mapper(dobj.ComponentEntry, component_table)

version_table = Table('versions', metadata
        column('id',Integer, primary_key=True, unique=True,
                auto_increment=True),
        column('name', String(__TAX_NAME_LENGTH__)),
        column('isdefault', Boolean),
)

mapper(dobj.VersionEntry, version_table)

milestone_table = Table('milestones', metadata
        column('id',Integer, primary_key=True, unique=True,
                auto_increment=True),
        column('name', String(__TAX_NAME_LENGTH__)),
        column('isdefault', Boolean),
)

mapper(dobj.MilestoneEntry, milestone_table)

severity_table = Table('severities', metadata
        column('id',Integer, primary_key=True, unique=True,
                auto_increment=True),
        column('name', String(__TAX_NAME_LENGTH__)),
        column('isdefault', Boolean),
)

mapper(dobj.SeverityEntry, severity_table)

priority_table = Table('priorities', metadata
        column('id',Integer, primary_key=True, unique=True,
                auto_increment=True),
        column('name', String(__TAX_NAME_LENGTH__)),
        column('isdefault', Boolean),
)

mapper(dobj.PriorityEntry, priority_table)

status_table = Table('status', metadata
        column('id',Integer, primary_key=True, unique=True,
                auto_increment=True),
        column('name', String(__TAX_NAME_LENGTH__)),
        column('isdefault', Boolean),
)

mapper(dobj.StatusEntry, status_table)

resolution_table = Table('resolutions', metadata
        column('id',Integer, primary_key=True, unique=True,
                auto_increment=True),
        column('name', String(__TAX_NAME_LENGTH__)),
        column('isdefault', Boolean),
)

mapper(dobj.ResolutionEntry, resolution_table)

##############################
# Upstream tracker definition
##############################
__URI_LENGTH__ = 200
upstream_table = Table('upstream', metadata
    column('id', Integer, primary_key=True, unique=True,
            auto_increment=True),
    column('uri', String(__URI_LENGTH__),
    column('type', Integer),
    column('authentication', PickleType), # blob containing auth info
    column('transport', PickleType), # blob containing transport info
)

mapper(dobj.Upstream, upstream_table)
