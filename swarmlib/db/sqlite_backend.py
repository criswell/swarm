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
import sys

import swarmlib.swarm_time
from swarmlib import swarm_error
import swarmlib.data_tools as data_tools
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
                if column.auto_increment and __sqlite_version__ >= 3: sql_code = sql_code + " AUTO_INCREMENT"
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

        # Add the first entry to the xlog
        # The 0th entry will always be the date stamp of when the issue tracker repo started
        self.log_transaction(__MASTER_ISSUE__, 'xlog_start', 'Null', 0)
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

    def log_transaction(self, root, xaction, xdata, setid=None):
        """
        log_transaction(root, xaction, xdata, setid=None)
        Log a given transaction.
        root = the root id of the issue this transaction corresponds to.
               Use __MASTER_ISSUE__ (imported from swarmlib.db) if this
               transaction is a change outside of any current issue.
        xaction = The transaction code. Use one of the codes in the
                  'transactions' dictionary imported from swarmlib.
                  If you need a new code added to this dictionary, please
                  discuss it before hand.
        xdata = The transaction data needed to recreate the xaction.
                Usually, it's best to pickle this to a string.
        setid = If this isn't set (the default) then the next log id
                will be used. This is the way you SHOULD use it.
                Occassionally, there will be a need where people *might*
                want to specify a specific log id. You can request one here,
                but the request may be ignored if the id isn't valid.
                Really... unless you're doing something wacky like creating
                a new repo or a new root issue, just leave this setting
                alone.
        """
        self._logger.register('_log_transaction')
        if self._connected:
            actual_db_version = self._config.get('sqlite', 'db_version', 'swarm')
            if actual_db_version == 2:
                # Stub to grow
                print "What you trying to pull here, there is no swarmdb version 2!"
                sys.exit(2)
            else:
                # Default is db_version 1
                timestamp = swarmlib.swarm_time.timestamp()
                rowid = "Null"
                if setid:
                    # Let's make sure you have a requested id that's larger than the max
                    self._cursor.execute("select max(id) from xlog;")
                    maxid = self._cursor.fetchcall()
                    if not maxid[0][0] or int(setid) > int(maxid[0][0]):
                        rowid = str(setid)
                    else:
                        self._logger.error("Requested id for xlog entry, '%s', was lower than the maxid, '%s'. Ignoring request." % (str(setid), str(maxid)))
                    rowid = str(setid)
                sql_code = "INSERT INTO xlog (id, root, time, xaction, xdata) VALUES (" + str(rowid) + ", " + str(root) + ", %f, %s, %s);"
                self._logger.entry("SQL code is:\n%s" % (sql_code % (float(timestamp), xaction, xdata)), 5)
                self._cursor.execute(sql_code, (float(timestamp), xaction, xdata))
        else:
            raise swarm_error('Transaction log entry attempted when not connected to database.')

        self._logger.unregister()

    def search_transaction_log(self, issue=None, lower_entry=None, upper_entry=None, lower_date=None, upper_date=None, xaction=None):
        """
        search_transaction_log(...)
        Get a transaction log slice. Accepts the following parameters:
        issue : If you don't specify an issue, will default to None (e.g., all entries)
        lower_entry : The lower log entry number to start at, will default to None (e.g., no lower limit)
        upper_entry : The upper log entry number to end at, will default to None (e.g., no upper limit)
        lower_date : The lower date to start at, will default to None (e.g., begining of time)
        upper_date : The upper date to end at, will default to None (e.g., the end of days)
        xaction : The transaction to filter by, will default to None

        If called with no parameters will just return the entire transaction log.
        """
        self._logger.register('search_transaction_log')
        args = [ issue, lower_entry, upper_entry, lower_date, upper_date, xaction]
        limit_text = [
            "root = %s"
            , "id > %s"
            , "id < %s"
            , "time > %s"
            , "time < %s"
            , "xaction = '%s'"
            ]
        clauses = [ clause % arg for clause,arg in zip(limit_text,args) if arg is not None ]
        query = "SELECT * FROM xlog"
        if clauses:
            query = query + " WHERE " + " AND ".join(clauses)

        self._logger.entry("SQL code is:\n%s" % query, 5)
        self._cursor.execute(query)
        result =  self._cursor.fetchall()
        self._logger.unregister()
        return result

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
            final_entries = [term]
            column_names = []
            column_values = []
            sql_code = ""
            sql_columns = ""
            for key in entry.keys():
                column_names.append(key)
                column_values.append(entry[key])

            first_entry = True
            for name in column_names:
                final_entries.append(name)
                if first_entry:
                    sql_columns = sql_columns + "%s"
                    first_entry = False
                else:
                    sql_columns = sql_columns + ", %s"

            for value in column_values:
                final_entries.append(value)

            # We've removed the error checker here, we need to put it back in
            # We no longer check to see if connected. FIXME
            sql_code = "REPLACE INTO %s (" + sql_columns + ") VALUES (" + sql_columns + ");"
            self._logger.entry("SQL code is:\n%s" % (sql_code % tuple(final_entries)), 5)
            self._cursor.execute(sql_code, tuple(final_entries))

        self.log_transaction(__MASTER_ISSUE__, 'set_taxonomy', data_tools.encode_content(the_list))

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

    def get_taxonomy_default(self, term):
        """
        Given a taxonomy name, will return the default
        value
        """
        self._logger.register("get_taxonomy_default")
        the_list = None

        sql_code = "SELECT * FROM %s WHERE isdefault=1;" % term
        self._logger.entry("Executing SQL code: '%s'" % sql_code, 5)
        if self._connected:
            self._cursor.execute(sql_code)
            the_list = self._convert_list(self._cursor.fetchall(), term)
        else:
            self._logger.error("Attempted to get taxonomy while not connected to the database. Could it be that the connection failed for some reason?")
            raise swarm_error("Attempted to get taxonomy while not connected to the database. Could it be that the connection failed for some reason?")
        self._logger.unregister()
        if len(the_list) == 1:
            return the_list[0]
        else:
            return None

    def _add_entry(self, table_name, table_data):
        """
        Internal add_entry function
        """
        self._logger.register("_add_entry")
        column_names = []
        column_values = []
        final_entries = []
        sql_code = ""
        sql_columns = ""
        sql_datatypes = ""

        table_in_use = None

        # First, get the schema:
        for table in table_schema:
            if table.name == table_name:
                table_in_use = table
                break

        first_entry = True
        for key_name in table_data.keys():
            column_names.append(key_name)
            local_type = '%s'
            #if key_name == 'id':
            #    column_values.append(None)
            if table_data[key_name]:
                (local_type, converted) = table_in_use.convert(key_name, table_data[key_name])
                column_values.append(converted)
            else:
                column_values.append(None)
            if first_entry:
                sql_datatypes = sql_datatypes + local_type
                first_entry = False
            else:
                sql_datatypes = sql_datatypes + ", %s" % local_type

        first_entry = True
        for name in column_names:
            final_entries.append(name)
            if first_entry:
                sql_columns = sql_columns + "%s"
                first_entry = False
            else:
                sql_columns = sql_columns + ", %s"

        for value in column_values:
            final_entries.append(value)

        # FIXME : We're not checking if we're connected here
        sql_code = "INSERT INTO " + table_name +" (" + sql_columns + ") VALUES (" + sql_datatypes + ");"
        self._logger.entry("SQL code is:\n%s" % (sql_code % tuple(final_entries)), 5)
        self._cursor.execute(sql_code, tuple(final_entries))

        self._logger.unregister()

    def new_node(self, node_data):
        """
        new_node(node_data):
        Given node_data, add to node table
        """
        self._add_entry('node', node_data)

    def new_issue(self, issue_data):
        """
        new_issue(issue_data)
        Given issue_data, add to issue table.
        Returns new issue id
        """
        issue_id = None
        self._logger.register("new_issue")

        # The ID needs to be None
        issue_data['id'] = None

        self._add_entry('issue', issue_data)

        sql_code = 'SELECT id FROM issue WHERE root_node="%s";' % issue_data['root_node']
        self._logger.entry("SQL code is:\n%s" % sql_code, 5)
        self._cursor.execute(sql_code)
        temp = self._cursor.fetchall()
        if temp[0][0]:
            issue_id = temp[0][0]

        if issue_id:
            self.log_transaction(issue_id, 'new_issue', issue_id)
        else:
            print "PROBLEM!"
            # FIXME: We should try to rollback I guess

        self._logger.entry("Created new issue #%s" % str(issue_id), 3)

        self._logger.unregister()
        return issue_id

    def get_next_free_id(self, table_name, id_string):
        """
        Given a table name and id string, will return the next free id
        available in that table. In SQL DBs this means max(id_string)
        FIXME - WE DON'T NEED THIS FUNCTION ANY MORE
        DELME DELME DELME
        """
        next_id = None
        self._logger.register("get_next_free_id")
        sql_code = "SELECT max(%s) FROM %s;" % (id_string, table_name)
        self._logger.entry("Executing SQL code: '%s'" % sql_code, 5)
        if self._connected:
            self._cursor.execute(sql_code)
            temp = self._cursor.fetchall()
            if temp[0][0]:
                next_id = temp[0][0]
            else:
                next_id = 1
        else:
            self._logger.error("Attempted to get taxonomy while not connected to the database. Could it be that the connection failed for some reason?")
            raise swarm_error("Attempted to get taxonomy while not connected to the database. Could it be that the connection failed for some reason?")

        self._logger.unregister()
        return next_id

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
            self._config.set('sqlite', 'db_subversion', __db_subversion__, 'swarm')

            self._config.save()
        else:
            self._logger.error("SQLite db '%s' file exists! (Use force to overwrite)" % self._db_filename)
            raise swarm_error("SQLite db '%s' file exists! (Use force to overwrite)" % self._db_filename)

        self._logger.unregister()
