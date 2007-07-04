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
import time
#import sqlite # Should do some more fanciness here, I'm sure
              # like, you know, try various versions and whatnot

from swarmlib import *
from swarmlib.db import table_schema
from swarmlib.db import table_defaults
from swarmlib.db import __db_version__
from swarmlib.db import __MASTER_ISSUE__

__db_subversion__ = None
__sqlite_version__ = None

try:
    import sqlite3 as sqlite
    __db_subversion__ = 2
    __sqlite_version__ = 3
except ImportError:
    try:
        import sqlite
        __db_subversion__ = 1
        __sqlite_version__ = 2
    except ImportError:
        __db_subversion__ = None
        __sqlite_version__ = None

class db:
    def __init__(self, cwd, config, log, force):
        self._db_filename = "%s/%s" % (config.dot_swarm, config.get('db', 'dbfile', 'swarm'))
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
            sql_code = "drop table %s;\n" % table.name
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

    def _prepopulate_tables(self):
        self._logger.register("_prepopulate_tables")
        for table in table_defaults.keys():
            for entry in table_defaults[table]:
                column_code = ""
                value_code = ""
                first_entry = True
                for key in entry.keys():
                    if first_entry:
                        first_entry = False
                    else:
                        column_code = column_code + ", "
                        value_code = value_code + ", "

                    column_code = column_code + "%s" % key
                    value_code = value_code + '"%s"' % entry[key]
                sql_code = "INSERT INTO %s (%s) VALUES (%s);\n" % (table, column_code, value_code)
                self._logger.entry("SQL code is:\n%s" % sql_code, 5)
                if self._connected:
                    self._cursor.execute(sql_code)
                else:
                    self._logger.error("Attempted to prepopulate table while not connected to the database. Could it be that the connection failed for some reason?")
                    raise swarm_error("Attempted to prepopulate table while not connected to the database. Could it be that the connection failed for some reason?")
        self._logger.unregister()

    def _convert_list(self, the_list, term):
        """
        Given an sqlite result and tablename will
        generate a list of dictionaries with column
        names and values
        """
        self._logger.register("_convert_list")
        converted_list = []

        table_in_use = None
        columns = []

        # First, get the schema:
        for table in table_schema:
            if table.name == term:
                table_in_use = table
                break

        if not table_in_use:
            raise swarm_error("No table named '%s'" % term)

        for column in table_in_use.columns:
            columns.append(column.name)

        # Now, let's convert the list using this schema
        for entry in the_list:
            if len(entry) != len(columns):
                self._logger.error("Table column mismatch in sqlite results from taxonomy query on '%s', database may be corrupt. Skipping." % term)
                continue

            converted_entry = {}
            for i in range(len(entry)):
                converted_entry[columns[i]] = entry[i]

            converted_list.append(converted_entry)

        return converted_list

        self._logger.unregister()

    def _log_transaction(self, root, xaction, xdata):
        """
        Internal function for logging the transaction into the
        sqlite table 'log'
        """
        self._logger.register('_log_transaction')
        if self._connected:
            # Determine what number we're on
            # by looking at the 0th entry
            print
            # BAH ERE I AM JH
            # get unique hash for id
            # get unique time in int utc
            # figure out sql code
            # enter it
        else:
            self._logger.error('Transaction log entry attempted when not connected to database. Skipping.')

        self._logger.unregister()

    def connect(self):
        """
        Connect to the database
        """
        self._logger.register("connect")
        self._logger.entry("Connecting to db file: %s" % self._db_filename, 5)
        if not self._connected:
            db_exists = os.path.isfile(self._db_filename)
            if db_exists:
                self._get_connection()
            else:
                self._logger.error("Cannot connect to database, file not found. Workspace not initialized?")
        else:
            self._logger.error("Connect was called after we were already connected.")
            raise swarm_error("Connect was called after we were already connected.")

        self._logger.unregister()


    def close(self):
        """
        Call this when you wish to close your connection to the db
        """
        self._connect.commit()
        self._connect.close()
        self._connected = False

    def set_taxonomy(self, term, the_list):
        """
        Given a table name, will update its contents with the new
        terms from 'the_list'
        """
        self._logger.register("set_taxonomy")

        for entry in the_list:
            column_names = ""
            column_values = ""
            first_entry = True
            for key in entry.keys():
                if first_entry:
                    column_names = column_names + key
                    column_values = '"%s"' % entry[key]
                    first_entry = False
                else:
                    column_names = column_names + ", " + key
                    column_values = '%s, "%s"' % (column_values, entry[key])
            sql_code = "REPLACE INTO %s (%s) VALUES (%s);" % (term, column_names, column_values)
            self._logger.entry("SQL code is:\n%s" % sql_code, 5)
            if self._connected:
                self._cursor.execute(sql_code)
            else:
                self._logger.error("Attempted to replace table entries while not connected to the database. Could it be that the connection failed for some reason?")
                raise swarm_error("Attempted to replace table entries while not connected to the database. Could it be that the connection failed for some reason?")

        self._logger.unregister()

    def get_taxonomy(self, term):
        """
        Given a table name, will return the list of the
        taxonomy that table describes
        """
        self._logger.register("get_taxonomy")
        the_list = None

        sql_code = "SELECT * FROM %s order by id;" % term
        self._logger.entry("Executing SQL code: '%s'" % sql_code, 5)
        if self._connected:
            self._cursor.execute(sql_code)
            the_list = self._convert_list(self._cursor.fetchall(), term)
        else:
            self._logger.error("Attempted to get taxonomy while not connected to the database. Could it be that the connection failed for some reason?")
            raise swarm_error("Attempted to get taxonomy while not connected to the database. Could it be that the connection failed for some reason?")
        self._logger.unregister()
        return the_list

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
            self._prepopulate_tables()
            self._config.add_section('sqlite', 'swarm')
            self._config.set('sqlite', 'db_version', __db_version__, 'swarm')
            self._config.save()
        else:
            self._logger.error("SQLite db '%s' file exists! (Use force to overwrite)" % self._db_filename)
            raise swarm_error("SQLite db '%s' file exists! (Use force to overwrite)" % self._db_filename)

        self._logger.unregister()