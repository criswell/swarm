#!/usr/bin/env python

# swarmlib.xlog - Transaction log abstraction layer
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

from swarmlib import *

__xlog_version__ = 1
__MASTER_LOG__ = 0

xlog_backends = {
    'cPickle' : 'cPickle backend',
}

class xlog:
    def __init__(self, config, log, force=False):
        """
        __init__(config, log, force=False)
        """
        self._config = config
        self._log = log
        self._logger = log.get_logger("xlog")
        self._force = force
        self._xlog = None
        self._master = None
        self.backend_type = self._config.get('xlog', 'type')
        self._load_backend()
        self._setup()

    def _load_backend(self):
        """
        Internal backend loader
        """
        self._logger.register("_load_backend")

        self._logger.entry("Loading '%s' backend" % self.backend_type, 2)
        self._xlog = import_at_runtime("swarmlib.xlog.%s" % xlog_backends[self.backend_type], "xlog")

        self._logger.unregister()

    def _setup(self):
        """
        Internal. Called to setup the xlog master.
        """
        self._logger.register("_setup")

        if self._xlog:
            self._master = self._xlog(__MASTER_LOG__, self._config, self._log)
        else:
            self._logger.error("_setup called before backend loaded. Did _load_backend fail?")
            raise swarm_error("_setup called before backend loaded. Did _load_backend fail?")

        self._logger.unregister()
