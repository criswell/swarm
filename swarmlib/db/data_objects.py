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
Swarm Data Objects

Contains all of the data objects defined and used by Swarm.
"""

# FIXME - Do we really want to just import everything?
from elixir import *

class Issue(Entity):
    using_options(tablename='issue')

    # The hash id for the issue
    hash_id = Field(String(128), required=True, unique=True, primary_key=True)

    # The shorter, human-readable issue id
    short_hash_id = Field(String(50), required=True, unique=True)

    # The summary field for the issue
    summary = Field(Unicode(256), required=True)

    # The date/time when this issue was reported
    report_time = Field(DateTime, required=True)

    # The last time this issue was changed
    change_time = Field(DateTime)

    # The issue can be any of a number of user defined types
    issue_type = OneToMany('IssueType')

    # The issue can be any of a number of user defined severity types
    severity_type = OneToMany('SeverityType')

    # The status of the issue
    status_type = OneToMany('StatusType')

    # The resolution of the issue
    resolution_type = OneToMany('ResolutionType')

    # The priority of the issue
    priority_type = OneToMany('PriorityType')

    # Associated version
    version = OneToMany('VersionEntry')

    # The original reporter of the issue
    # FIXME -
    # Should this use the same sort of many to many mapping as followers?
    reporter = Field(Unicode(128), require=True)

    # The owner of the issue
    owner = Field(Unicode(128), require=True)

    # Keyword lookups
    keywords = ManyToMany('Keyword')

    # Followers
    followers = ManyToMany('Follower')

    def __repr__(self):
       return "<Issue('%s', '%s')>" % (self.hash_id, self.short_hash_id)

class Follower(Entity):
    using_options(tablename='follower')

    name = Field(Unicode(128), require=True)

    email = Field(Unicode(128))

    issue = ManyToMany('Issue')

    def __repr__(self):
        return "<Follower('%s', '%s')>" % (self.name, self.email)

class Keyword(Entity):
    using_options(tablename='keyword')

    keyword = Field(Unicode(50)

    issues = ManyToMany('Issue')

    def __repr__(self):
        return "<Keyword('%s')>" % (self.keyword)

class VersionEntry(Entity):
    using_options(tablename='version')

    # The human-readable name for this version
    name = Field(Unicode(100, required=True, unique=True)

    # optional description for this version
    description = Field(UnicodeText)

    # whether this should be a default version or not
    is_default = Field(Boolean, required=True)

    # issue mapping
    issue = ManyToOne('Issue')

    def __repr__(self):
        return "<VersionEntry('%s', default:'%s')>" % (self.name,
                self.is_default)

class PriorityType(Entity):
    using_options(tablename='priority_type')

    # The human-readable name for this priority type
    type_name = Field(Unicode(100, required=True, unique=True)

    # optional description for this priority type
    type_description = Field(UnicodeText)

    # whether this should be a default priority or not
    is_default = Field(Boolean, required=True)

    # issue mapping
    issue = ManyToOne('Issue')

    def __repr__(self):
        return "<PriorityType('%s', default:'%s')>" % (self.type_name,
                self.is_default)

class ResolutionType(Entity):
    using_options(tablename='resolution_type')

    # The human-readable name for this resolution type
    type_name = Field(Unicode(100, required=True, unique=True)

    # optional description for this resolution type
    type_description = Field(UnicodeText)

    # whether this should be a default resolution or not
    is_default = Field(Boolean, required=True)

    # issue mapping
    issue = ManyToOne('Issue')

    def __repr__(self):
        return "<ResolutionType('%s', default:'%s')>" % (self.type_name,
                self.is_default)

class SeverityType(Entity):
    using_options(tablename='severity_type')

    # The human-readable name for this severity type
    type_name = Field(Unicode(100, required=True, unique=True)

    # optional description for this severity type
    type_description = Field(UnicodeText)

    # whether this should be a default severity or not
    is_default = Field(Boolean, required=True)

    # issue mapping
    issue = ManyToOne('Issue')

    def __repr__(self):
        return "<SeverityType('%s', default)>" % (self.type_name,
                self.is_default)

class StatusType(Entity):
    using_options(tablename='status_type')

    # The human-readable name for this status type
    type_name = Field(Unicode(100, required=True, unique=True)

    # optional description for this status type
    type_description = Field(UnicodeText)

    # whether this should be a default status or not
    is_default = Field(Boolean, required=True)

    # issue mapping
    issue = ManyToOne('Issue')

    def __repr__(self):
        return "<StatusType('%s', default)>" % (self.type_name,
                self.is_default)

class IssueType(Entity):
    using_options(tablename='issue_type')

    # The name for this issue type
    type_name = Field(Unicode(100, required=True, unique=True)

    # Optional description for this issue type
    type_description = Field(UnicodeText)

    issue = ManyToOne('Issue')

    def __repr__(self):
        return "<IssueType('%s')>" % (self.type_name)

class Node(object):
    def __init__(self, hash_id, summary):
        self.hash_id = hash_id
        self.summary = summary
    def __repr__(self):
        return "<Node('%s', '%s')>" % (self.hash_id, self.summary)

class TransactionEntry(object):
    def __init__(self, root, time, transaction, transaction_data):
        self.root = root
        self.time = time
        self.transaction = transaction
        self.transaction_log = transaction_log

    def __repr__(self):
        return "<TransactionEntry(root:'%s', time:'%s'>" % (self.root,
                self.time)

class ComponentEntry(object):
    def __init__(self, name, isdefault=False):
        self.name = name
        self.isdefault = isdefault

    def __repr__(self):
        return "<ComponentEntry('%s', default:'%s')>" % (self.name,
                self.isdefault)

class MilestoneEntry(object):
    def __init__(self, name, isdefault=False):
        self.name = name
        self.isdefault = isdefault

    def __repr__(self):
        return "<MilestoneEntry('%s', default:'%s')>" % (self.name,
                self.isdefault)

class Upstream(object):
    def __init__(self, uri, upstream_type, authentication, transport):
        self.uri = uri
        self.upstream_type = upstream_type
        self.authentication = authentication
        self.transport = transport

    def __repr__(self):
        return "<Upstream('%s')>" % self.uri
