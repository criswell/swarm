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
import ConfigParser

class config:
    def __init__(self, cwd, log, force=False):
        self.project_root = cwd
        self.dot_swarm = "%s/.swarm" % self.project_root
        self.system_configparser = ConfigParser.ConfigParser()
        self.user_configparser = ConfigParser.ConfigParser()
        self.swarm_configparser = ConfigParser.ConfigParser()
        self._swarm_config_is_set = False
        self._force = force
        self._logger = log.get_logger("config")
        self._load_config()

    def _load_config(self):
        # load the configuration

        self._logger.register("_load_config")

        # Read the system-wide config file (if exists)
        # Will run through these sequentially, first one
        # to exist wins
        system_configs = ['/etc/swarm.conf',
                          '/etc/swarm/swarm.conf',
                          '/etc/swarmd/swarm.conf'
                         ]

        self._logger.entry("Attempting to load system-wide config", 2)

        filenames_read = self.system_configparser.read(system_configs)

        if len(filenames_read):
            self._logger.enty("Read the following system-wide config files", 3)
            for filename in filenames:
                self._logger.entry(filename, 3)

        # Read the user config file
        self._logger.entry("Attempting to read user config", 2)

        user_config = "%s/.swarm" % (os.path.expanduser("~"))
        if os.path.isfile(user_config):
            self._logger.entry("Attemping to load user config %s" % user_config, 2)
            self.user_configparser.read(user_config)
        else:
            self._logger.entry("No user config file found. If you want to set user settings use '%s'" % user_config, 1)

        # Read the swarm config file (per project)
        swarm_config = "%s/swarmrc" % self.dot_swarm
        self._logger.entry("Attempting to read swarm config %s" % swarm_config, 2)

        if os.path.isfile(swarm_config):
            self.swarm_configparser.read(swarm_config)
            self._swarm_config_is_set = True
        else:
            self._logger.entry("swarm config does not exist.", 2)
            self._swarm_config_is_set = False

        self._logger.unregister()

    def init(self, project_name):
        """ init project config file """

        self._logger.register("init")

        swarm_config = "%s/swarmrc" % self.dot_swarm
        if self._swarm_config_is_set:
            self._logger.error("swarm config is already set for project root '%s'" % self.project_root)
            if not self._force:
                sys.exit(2)
            self._logger.error("initializing anyway because of 'force' option")

        project_root_exists = os.path.exists(self.project_root)
        if not project_root_exists:
            self._logger.entry("Attempting to create project root '%s'", % self.project_root, 2)
            try:
                os.mkdir(self.project_root)
            except:
                self._logger.error("Could not create project root '%s'. Does parent exist and do you have permissions to create this?" % self.project_root)
                sys.exit(2)

        dot_swarm_exists = os.path.exists(self.dot_swarm)
        if not dot_swarm_exists:
            self._logger.entry("Attempting to create dot swarm directory '%s'", % self.dot_swarm, 2)
            try:
                os.mkdir(self.dot_swarm)
            except:
                self._logger.error("Could not create directory '%s'. Does parent exist and do you have permissions to create this?" % self.project_root)
                sys.exit(2)

        swarmrc_exists = os.path.isfile(swarm_config)
        if not swarmrc_exists:
            self._logger.entry("Attempting to create swarm rc '%s'", % swarm_config, 2)
            dbfile = "%s/swarm.db" % self.dot_swarm
            self.swarm_configparser.add_section("main")
            self.swarm_configparser.set("main", "project_name", project_name)
            self.swarm_configparser.set("main", "dbfile", dbfile)
            self.swarm_configparser.set("main", "dbtype", "sqlite")

            fp = open(swarm_config, mode="w")
            self.swarm_configparser.write(fp)
            fp.close()
            selt._swarm_config_is_set = True

        self._logger.unregister()

    def get(self, section, setting, config_region=None):