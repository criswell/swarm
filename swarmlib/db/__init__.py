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

        column('parents'),
        column('children'),
        column('related'),
    ],

    table('issue_custom')[
        column('id'),
        column('name'),
        column('value'),
    ],

    #root tracker
    table('rootids')[
        column('humanid'),
        column('id'),
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

database_backends = {
    'sqlite' : 'sqlite_backend',
}

class swarmdb:
    def __init__(self, project_root, config, log, force=False):
        self._config = config
        self._log = log
        self._logger = log.get_logger("swarmdb")
        self._force = force
        self._project_root = project_root
        self.backend = None
        self._backend_class = None
        self.backend_type = self._config('main', 'dbtype')
        self._load_backend()

    def _load_backend(self):
        self._logger.register("_load_backend")

        self._logger.entry("Loading '%s' backend" % self.backend_type, 2)
        self._backend_class = import_at_runtime("swarmlib.swarmdb", database_backend[self.backend_type])
        self.backend = self._backend_class(self._project_root, self._config, self._log, self._force)