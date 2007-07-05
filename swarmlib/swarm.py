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
from swarmlib.db import __MASTER_ISSUE__

def master_init(project_name, working_dir, log, force=False):
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

        self._setup()

    def _setup(self):
        """
        Internal setup function
        """
        self._logger.register("_setup")

        self.config = Config.config(self._working_dir, self._log)
        self.db = swarmdb(self._working_dir, self._config, self._log)
        self.db.backend.connect()

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
        # TODO, we should probably do some error checking here
        self._set_taxonomy(term, the_list)

    def get_transaction_log(self, issue=None, lower_entry=None, upper_entry=None, lower_date=None, uppder_date=None, xaction=None):
        """
        get_transaction_log(...)
        Get a transaction log slice. Accepts the following parameters:
        issue : If you don't specify an issue, will default to None (e.g., all entries)
        lower_entry : The lower log entry number to start at, will default to None (e.g., no lower limit)
        upper_entry : The upper log entry number to end at, will default to None (e.g., no upper limit)
        lower_date : The lower date to start at, will default to None (e.g., begining of time)
        upper_date : The upper date to end at, will default to None (e.g., the end of days)
        xaction : The transaction to filter by, will default to None

        If called with no parameters will just return the entire transaction log.

        The most common use for this will be to find changes to the repo or to individual
        issues. For example, let's say there's an external repo that is wanting to sync
        with us. The last time they synced was at log entry #871, and they are requesting
        all the changes since then. This function would be called as:
          get_transaction(lower_entry=871)

        easy, no?

        Okay, let's next suppose that we have an external repo that is tracking issue #45
        on our repo. They haven't synced since log entry #4711, so they want all changes
        since then for issue #45 only. The function would be called as:
          get_transaction(issue=45, lower_entry=4711)

        Anyway... there's more you can do with dates and things, but I wont go into that
        here.
        """
        self._logger.register("get_transaction_log")

        self._logger.unregister()

    def close(self):
        """
        Closes the database (syncronizing data) as well as all
        open xlog files.
        """
        self.db.backend.close()
