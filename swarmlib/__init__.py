#!/usr/bin/env python

# swarmlib - Main swarmlib module
#
# Copyright 2007 Sam Hart
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Author: Sam Hart

import swarmlib.config as Config
from swarmlib.db import swarmdb
from swarmlib.db import taxonomy_terms

class swarm_error(Exception):
    def __init__(self, message, show_traceback=False):
        Exception.__init__(self, message)
        self.message = message
        self.show_traceback = show_traceback

def import_at_runtime(module_name, suite_name):
    """
    Imports a python module determined at runtime.
    """
    try:
        module = __import__(module_name, globals(), locals(), [suite_name])
    except ImportError:
        return None
    return vars(module)[suite_name]

def master_init(working_dir, log, force=False):
    """
    master_init(working_dir, log, force=False)
    This is called when an issue repository is to be
    initialized for the first time.
    Use force=True to overwrite any existing issue
    repository elements that may be found.
    """
    config = Config.config(working_dir, log, force)
    config.init(project_name)
    db = swarmdb(working_dir, config, log, force)
    db.backend.init()
    db.backend.close()
    xlog = Xlog(config, log, force)

# FIXME : These 'None's should be set to callbacks when we get them
transactions = {
    'xlog_start' : None,
    'set_taxonomy' : None,
}

class swarm:
    def __init__(self, working_dir, log, force=False):
        """
        __init__(working_dir, log, force=False)
        Main swarm class interface for all the nastiness
        that goes on behind the scene.
        """
        self._working_dir = working_dir
        self._log = log
        self._force = force
        self._logger = log.get_logger("swarm")
        self.config = None
        self.db = None
        self.xlog = None

        self._setup()

    def _setup(self):
        """
        Internal setup function
        """
        self._logger.register("_setup")

        self.config = Config.config(self._working_dir, self._log)
        self.db = swarmdb(self._working_dir, self._config, self._log)
        self.db.backend.connect()
        self.xlog = Xlog(self._config, self._log, self._force)

        self._logger.unregister()

    def get_taxonomy(self, tax_term):
        """
        Given a table name, will return the list of the
        taxonomy that table describes
        """
        return self.db.backend.get_taxonomy(tax_term)

    def _set_taxonomy(self, term, the_list):
        """
        INTERNAL FUNCTION, DONT CALL
        Given a table name, will update its contents with the new
        terms from 'the_list'
        """
        self.db.backend.set_taxonomy(term, the_list)

    def set_taxonomy(self, term, the_list):
        """
        Given a table name, will update its contents with the new
        terms from 'the_list'
        """
        # LOG TRANSACTION HERE TODO
        self._set_taxonomy(term, the_list)

    def close(self):
        """
        Closes the database (syncronizing data) as well as all
        open xlog files.
        """
        self.db.backend.close()
        # TODO: Need routine for closing xlogs
