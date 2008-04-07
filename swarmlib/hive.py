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
The Swarm Hive "super" class

This class houses the most common Swarm Hive interactions.
"""

import urlparse

class Hive(object):
    def __init__(self, url, log, Force=False, config=None):
        """
        Basic URL parsing wrapper class
        Accessable members:
         .scheme = The scheme in use
         .netloc = The network location
         .path = The path
         .params = Parameters for path element
         .query = Query component
         .fragment = fragment identifier
         .username = username to use (if authentication is needed)
         .password = password to use (if authentication is needed)
         .hostname = hostname
         .port = port
        """
        self.url = url
        self._parsed = urlparse(url)
        self.scheme = self._parsed.scheme.lower()
        self.netloc = self._parsed.netloc
        self.path = self._parsed.path
        self.params = self._parsed.params
        self.query = self._parsed.query
        self.fragment = self._parsed.fragment
        self.username = self._parsed.username
        self.password = self._parsed.password
        self.hostname = self._parsed.hostname
        self.port = self._parsed.port
        self.connected = False
        self.connection = None
        self._log = log
        self._alt_config_file = config
        self.config = None
        self.force = force
        self._logger = log.get_logger("Hive")

    def init_hive(self, force=False, ):
        """
        Called when a new Hive is to be initialized
        """

    def connect(self):
        """
        Connects to the Hive.

        Returns nothing on success, otherwise raises an exception.
        """
        try:
            self.connection = connect.get_connection(self._parsed, self._log,
                                                     self.force)
        except:
            pass

        self.config = self.connection.get_config()

        self.connected = True
