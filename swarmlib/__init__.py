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
from swarmlib.xlog import xlog as Xlog
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

class swarm:
    def __init__(self,