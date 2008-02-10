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

from urlparse import urlparse

repo_backends = {
    'http' : 'http_backend',
}

class remote:
    def __init__(self, repo, log):
        self._log = log
        self._logger = log.get_logger("remote")
        self._repo = repo
        self._backend_class = None
        self._load_backend()

    def _load_backend(self):
        self._logger.register("_load_backend")

        self._logger.entry("Loading '%s' backend" % self._repo.scheme, 2)
        if self._repo.scheme in repo_backends.keys():
            mod_to_load = "swarmlib.remote.%s" % repo_backends[self._repo.scheme]
            self._logger.entry("Loading '%s'" % mod_to_load, 5)
            self._backend_class = import_at_runtime(mod_to_load, "remote")
            self.backend = self._backend_class(self._repo, self._config, self._log)
        else:
            self._logger.error("Remote scheme '%s' unsupported" % self._repo.scheme)

        self._logger.unregister()
