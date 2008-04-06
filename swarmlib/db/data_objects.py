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

#from sqlalchemy.orm import mapper, relation, backref

#import swarmlib.db.schema as schema

class Issue(object):
    def __init__(self, hash_id, short_hash_id):
        self.issue_id = short_hash_id
        self.hash_id = hash_id
    def __repr__(self):
       return "<Issue('%s', '%s')>" % (self.hash_id, self.short_hash_id)

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

class VersionEntry(object):
    def __init__(self, name, isdefault=False):
        self.name = name
        self.isdefault = isdefault

    def __repr__(self):
        return "<VersionEntry('%s', default:'%s')>" % (self.name,
                self.isdefault)

class MilestoneEntry(object):
    def __init__(self, name, isdefault=False):
        self.name = name
        self.isdefault = isdefault

    def __repr__(self):
        return "<MilestoneEntry('%s', default:'%s')>" % (self.name,
                self.isdefault)

class SeverityEntry(object):
    def __init__(self, name, isdefault=False):
        self.name = name
        self.isdefault = isdefault

    def __repr__(self):
        return "<SeverityEntry('%s', default:'%s')>" % (self.name,
                self.isdefault)

class PriorityEntry(object):
    def __init__(self, name, isdefault=False):
        self.name = name
        self.isdefault = isdefault

    def __repr__(self):
        return "<PriorityEntry('%s', default:'%s')>" % (self.name,
                self.isdefault)

class StatusEntry(object):
    def __init__(self, name, isdefault=False):
        self.name = name
        self.isdefault = isdefault

    def __repr__(self):
        return "<StatusEntry('%s', default:'%s')>" % (self.name,
                self.isdefault)

class ResolutionEntry(object):
    def __init__(self, name, isdefault=False):
        self.name = name
        self.isdefault = isdefault

    def __repr__(self):
        return "<ResolutionEntry('%s', default:'%s')>" % (self.name,
                self.isdefault)

class Upstream(object):
    def __init__(self, uri, upstream_type, authentication, transport):
        self.uri = uri
        self.upstream_type = upstream_type
        self.authentication = authentication
        self.transport = transport

    def __repr__(self):
        return "<Upstream('%s')>" % self.uri
