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
from swarmlib.db import __db_version__

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
        self._connected = False

    def _create_table(self):
        for table in table_schema:
            sql_code = "create table %s\n" % table.name
            sql_code = sql_code + "("
            first = True
            for column in table.columns:
                if not first:
                    sql_code = sql_code + ",\n"
                else:
                    sql_code = sql_code + "\n"
                    first = False
                sql_code = sql_code + column.name
                if column.data_type: sql_code = sql_code + " %s" % column.data_type
                if column.primary_key: sql_code = sql_code + " PRIMARY KEY"
                if column.auto_increment: sql_code = sql_code + " AUTO_INCREMENT"
                if column.unique: sql_code = sql_code + " UNIQUE"
            sql_code = sql_code +"\n);\n"
            self._logger.entry("SQL code is:\n%s" % sql_code, 5)
            if self._connected:
                self._cursor.execute(sql_code)
            else:
                self._logger.error("Attempted to create a table while not connected to the database. Could it be that the connection failed for some reason?")
                raise swarm_error("Attempted to create a table while not connected to the database. Could it be that the connection failed for some reason?")

    def _get_connection(self):
        self._connect = sqlite.connect(self._db_filename)
        self._cursor = self._connect.cursor()
        self._connected = True

    def close(self):
        self._connect.commit()
        self._connect.close()
        self._connected = False

    def init(self):
        self._logger.register("init")

        db_exists = os.path.isfile(self._db_filename)
        if db_exists and self._force:
            self._logger.entry("removing old database", 1)
            os.remove(self._db_filename)
            db_exists = False
        if not db_exists:
            self._logger.entry("connecting to database", 3)
            self._get_connection()
            self._create_table()
            self._config.add_section('sqlite', 'swarm')
            self._config.set('sqlite', 'db_version', __db_version__, 'swarm')
            self._config.save()
        else:
            self._logger.error("SQLite db '%s' file exists! (Use force to overwrite)" % self._db_filename)
            raise swarm_error("SQLite db '%s' file exists! (Use force to overwrite)" % self._db_filename)

        self._logger.unregister()