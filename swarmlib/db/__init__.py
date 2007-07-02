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

from swarmlib import *
#
# Database schema
#

__db_version__ = 1

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
        column('id', data_type='INTEGER', unique=True),

        column('component'),
        column('version'),
        column('milestone'),

        column('severity'),
        column('priority'),

        column('owner'),
        column('reporter'),
        column('cc'),
        column('subscribers'),

        column('keywords'),

        column('status'),
        column('resolution'),

        column('time', data_type='INTEGER'),
    ]

    table('node')[
        column('node_id', unique=True),
        column('time', data_type='INTEGER'),
        column('root'),

        column('parents'),
        column('children'),
        column('related'),

        column('summary'),
        column('details'),
        column('keywords'),

        column('attachments', data_type='blob'), #Should these be a seperate table?
    ],

    table('issue_custom')[
        column('node_id'),
        column('name'),
        column('value'),
    ],

    #upstream tracker
    table('upstream')[
        column('id'),
        column('uri'),
        column('type'),
        column('authentication', data_type='blob'), # blob containing auth info
        column('transport', data_type='blob'), # blob containing transport info
    ],

    #taxonomy
    table('component')[
        column('id', unique=True),
        column('name'),
        column('details'),
    ],

    table('version')[
        column('id', unique=True),
        column('name'),
        column('details'),
    ],

    table('milestone')[
        column('id', unique=True),
        column('name'),
        column('details'),
    ],

    table('severity')[
        column('id', unique=True),
        column('name'),
        column('isdefault', data_type='INTEGER'),
    ],

    table('priority')[
        column('id', unique=True),
        column('name'),
        column('isdefault', data_type='INTEGER'),
    ],

    table('status')[
        column('id', unique=True),
        column('name'),
        column('isdefault', data_type='INTEGER'),
    ],

    table('resolution')[
        column('id', unique=True),
        column('name'),
        column('isdefault', data_type='INTEGER'),
    ],
]

# The following tables will have some
# useful defaults. They can be overwritten.
table_defaults = {
    "severity" : [
        {'id' : 1,
        'name' : 'blocker',
        'isdefault' : 0},
        {'id' : 2,
        'name' : 'critical',
        'isdefault' : 0},
        {'id' : 3,
        'name' : 'major',
        'isdefault' : 0},
        {'id' : 4,
        'name' : 'normal',
        'isdefault' : 1},
        {'id' : 5,
        'name' : 'minor',
        'isdefault' : 0},
        {'id' : 6,
        'name' : 'trivial',
        'isdefault' : 0},
        {'id' : 7,
        'name' : 'enhancement',
        'isdefault' : 0},
    ],
    "priority" : [
        {'id' : 1,
        'name' : 'highest',
        'isdefault' : 0},
        {'id' : 2,
        'name' : 'high',
        'isdefault' : 0},
        {'id' : 3,
        'name' : 'medium',
        'isdefault' : 1},
        {'id' : 4,
        'name' : 'low',
        'isdefault' : 0},
        {'id' : 5,
        'name' : 'lowest',
        'isdefault' : 0},
    ],
    "status" : [
        {'id' : 1,
        'name' : 'unassigned',
        'isdefault' : 0},
        {'id' : 2,
        'name' : 'assigned',
        'isdefault' : 0},
        {'id' : 3,
        'name' : 'closed',
        'isdefault' : 0},
        {'id' : 4,
        'name' : 'new',
        'isdefault' : 1},
    ],
    "resolution" : [
        {'id' : 1,
        'name' : 'fixed',
        'isdefault' : 0},
        {'id' : 2,
        'name' : 'wontfix',
        'isdefault' : 0},
        {'id' : 3,
        'name' : 'invalid',
        'isdefault' : 0},
        {'id' : 4,
        'name' : 'worksforme',
        'isdefault' : 0},
        {'id' : 5,
        'name' : 'duplicate',
        'isdefault' : 0},
        {'id' : 6,
        'name' : 'none',
        'isdefault' : 1},
    ],
    "component" : [
        {'id': 0,
        'name': "None",
        'details' : 'No component'},
    ],
}

database_backends = {
    'sqlite' : 'sqlite_backend',
}

taxonomy_terms = ['component', 'version', 'milestone']

class swarmdb:
    def __init__(self, project_root, config, log, force=False):
        self._config = config
        self._log = log
        self._logger = log.get_logger("swarmdb")
        self._force = force
        self._project_root = project_root
        self.backend = None
        self._backend_class = None
        self.backend_type = self._config.get('db', 'type')
        self._load_backend()

    def _load_backend(self):
        self._logger.register("_load_backend")

        self._logger.entry("Loading '%s' backend" % self.backend_type, 2)
        self._backend_class = import_at_runtime("swarmlib.db.%s" % database_backends[self.backend_type], "db")
        self.backend = self._backend_class(self._project_root, self._config, self._log, self._force)

        self._logger.unregister()