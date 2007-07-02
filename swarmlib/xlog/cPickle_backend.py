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

import cPickle

from swarmlib.xlog import __xlog_version__
from swarmlib.xlog import __MASTER_LOG__

class xlog:
    def __init__(self, issue_number, config, log):
        """
        __init__(issue_number, config, log)
        cPickle backend for xlog
        """
        self.issue_number = issue_number
        self._config = config
        self._xlog_file = "%s/%s/%s.xlog" % (config.dot_swarm, config.get('main', 'xlog', 'directory'), str(issue_number))
        self._log = log
        self._logger = log.get_logger("cPickle_backend(xlog)")
        self.xlog = []
        self._init_xlog()

    def _init_xlog(self):
        """
        Internal command
        Initalizes the xlog file
        """
        self._logger.register("_init_xlog")

        if os.path.isfile(self._xlog_file):
            fp = open(self._xlog_file, "rb")
            self.xlog = cPickle.load(fp)
            fp.close()
        else:
            self.xlog = []
            fp = open(self._xlog_file, "wb")
            p = cPickle.Pickler(fp)
            p.dump(self.xlog)
            fp.close()

        self._logger.unregister()
