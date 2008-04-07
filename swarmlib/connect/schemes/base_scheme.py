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

"""
Swarm Connection Schemes: Base Scheme class

This contains the base scheme class by which all schemes are derived
"""

from swarmlib.config import Config

class BaseScheme(object):
    def __init__(self, parsed_url, config, log, force=False):
        self._parsed_url = parsed_url
        self._config = config
        self._force = force
        self._log = log

    def get_config(self):
        """
        The BaseScheme defaults to local directories. Overwrite if you
        don't want this
        """
        cwd = self._parsed_url.path
        self._config = Config(cwd, self._log, self._force)
        return self._config
