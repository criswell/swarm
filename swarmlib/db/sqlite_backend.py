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

import os
import sqlite # Should do some more fanciness here, I'm sure
              # like, you know, try various versions and whatnot

from swarmlib import *
from swarmlib.db import table_schema

class db:
    def __init__(self, cwd, config, log, force):
        self._db_filename = config.get('main', 'dbfile', 'swarm')
        self._project_root = cwd
        self._config = config
        self._log = log
        self._force = force
        self._logger = log.get_logger("sqlite_backend(db)")
        self._connect = None
        self._cursor = None

    def _create_table(self):
        for table in table_schema:
            print "Table '%s'" % table.name
            print "-------------------------------------------"
            columns = "|"
            for column in table.columns:
                columns = columns + (" %s |" % column.name)
            print columns

    def init(self):
        self._logger.register("init")

        db_exists = os.path.isfile(self._db_filename)
        if db_exists and self._force:
            self._logger.entry("removing old database", 1)
            os.remove(self._db_filename)
            db_exists = False
        if not db_exists:
            self._logger.entry("connecting to database", 3)
            self._connect = sqlite.connect(self._db_filename)
            self._create_table()
        else:
            self._logger.error("SQLite db '%s' file exists! (Use force to overwrite)" % self._db_filename)
            raise swarm_error("SQLite db '%s' file exists! (Use force to overwrite)" % self._db_filename)

        self._logger.unregister()