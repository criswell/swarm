# swarmlib.config - The config abstraction layer for swarmlib.
# Use this module to interface with swarmrc and config files.
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

"""
Swarm Config class definition

This module contains the Config(..) class for Swarm which interfaces with
any config file natively on the filesystem.
"""

import os
import sys
import ConfigParser

class Config(object):
    def __init__(self, cwd, log, force=False):
        """
        Main config class
        cwd = The current working directory or project root
        log = The log instance for the current running swarm program
        force = Whether operations performed by the config class
                should be forced
        """
        self.project_root = cwd
        self.dot_swarm = "%s/.swarm" % self.project_root
        self._config = {}
        # This is important for preference order
        # swarm>user>system
        # The last entry in this list will be the highest
        # priority
        self._config['regions'] = ['system', 'user', 'swarm']
        self._config['system'] = ConfigParser.ConfigParser()
        self._config['user'] = ConfigParser.ConfigParser()
        self._config['swarm'] = ConfigParser.ConfigParser()
        self.config_set = False
        self._force = force
        self._logger = log.get_logger("config")
        self._load_config()

    def _load_config(self):
        """
        Internal load config method.
        SHOULD NOT BE CALLED EXTERNALLY
        """
        self._logger.register("_load_config")

        # Read the system-wide config file (if exists)
        # Will run through these sequentially, first one
        # to exist wins
        system_configs = ['/etc/swarm.conf',
                          '/etc/swarm/swarm.conf',
                          '/etc/swarmd/swarm.conf'
                         ]

        self._logger.entry("Attempting to load system-wide config", 2)

        filenames_read = self._config['system'].read(system_configs)

        if len(filenames_read):
            self._logger.enty("Read the following system-wide config files", 3)
            for filename in filenames:
                self._logger.entry(filename, 3)

        # Read the user config file
        self._logger.entry("Attempting to read user config", 2)

        user_config = "%s/.swarm" % (os.path.expanduser("~"))
        if os.path.isfile(user_config):
            self._logger.entry("Attemping to load user config %s" % user_config, 2)
            self._config['user'].read(user_config)
        else:
            self._logger.entry("No user config file found. If you want to set user settings use '%s'" % user_config, 1)

        # Read the swarm config file (per project)
        swarm_config = "%s/swarmrc" % self.dot_swarm
        self._logger.entry("Attempting to read swarm config %s" % swarm_config, 2)

        if os.path.isfile(swarm_config):
            self._config['swarm'].read(swarm_config)
            self.config_set = True
        else:
            self._logger.entry("swarm config does not exist.", 2)
            self.config_set = False

        self._logger.unregister()

    def init(self, project_name, project_hash):
        """
        init project config file
        Given the "project_name" and "project_hash will initialize the
        project's swarmrc file.

        This should be called when a new project is being
        initialized.

        If the force setting was set to true in the class
        __init__ method, this method will overwrite the
        project's swarmrc file even if it exists.
        """

        self._logger.register("init")

        swarm_config = "%s/swarmrc" % self.dot_swarm
        if self.config_set:
            self._logger.error("swarm config is already set for project root '%s' (use force if you really want to overwrite)" % self.project_root)
            if not self._force:
                sys.exit(2)
            self._logger.error("initializing anyway because of 'force' option")
            os.remove(swarm_config)
            for section in self._config['swarm'].sections():
                self._config['swarm'].remove_section(section)

        project_root_exists = os.path.exists(self.project_root)
        if not project_root_exists:
            self._logger.entry("Attempting to create project root '%s'" % self.project_root, 2)
            try:
                os.mkdir(self.project_root)
            except:
                self._logger.error("Could not create project root '%s'. Does parent exist and do you have permissions to create this?" % self.project_root)
                sys.exit(2)

        dot_swarm_exists = os.path.exists(self.dot_swarm)
        if not dot_swarm_exists:
            self._logger.entry("Attempting to create dot swarm directory '%s'" % self.dot_swarm, 2)
            try:
                os.mkdir(self.dot_swarm)
            except:
                self._logger.error("Could not create directory '%s'. Does parent exist and do you have permissions to create this?" % self.project_root)
                sys.exit(2)

        swarmrc_exists = os.path.isfile(swarm_config)
        if not swarmrc_exists:
            self._logger.entry("Attempting to create swarm rc '%s'" % swarm_config, 2)
            #dbfile = "%s/swarm.db" % self.dot_swarm
            # This was, perhaps, not a good idea
            self._config['swarm'].add_section("main")
            self._config['swarm'].set("main", "project_name", project_name)
            self._config['swarm'].set("main", "project_hash", project_hash)

            # The following are defaults which we should
            # eventually allow to be overwritten via
            # system-wide or user settings, but for now,
            # we don't
            # FIXME
            self._config['swarm'].add_section('db')
            self._config['swarm'].set("db", "dbfile", "swarm.db")
            self._config['swarm'].set("db", "type", "sqlite")

            fp = open(swarm_config, mode="w")
            self._config['swarm'].write(fp)
            fp.close()
            self.config_set = True

        self._logger.unregister()

    def get(self, section, setting, config_region=None):
        """
        Get a given config's setting
        section = The section title of the config file
        setting = The setting we want the value for
        config_region = The config region to look up

        config_region can be one of 'system' (or system-
        wide settings), 'user' (or user-specific settings),
        or 'swarm' (project-specific settings).

        If config_region is not specified, will cycle
        through each config file taking the one from the
        highest priority file, e.g.,
            'system' < 'user' < 'swarm'
        """
        local_regions = self._config['regions']
        result = None
        if config_region and config_region in local_regions:
            local_regions = [config_region]

        for region in local_regions:
            if self._config[region].has_section(section):
                result = self._config[region].get(section, setting)

        return result

    def set(self, section, setting, value, config_region=None):
        """
        Set a specific config's setting
        section = The section title of the config file
        setting = The setting we want the value for
        value = The value to set setting to
        config_region = The config region to look up

        config_region can be one of 'system' (or system-
        wide settings), 'user' (or user-specific settings),
        or 'swarm' (project-specific settings).

        If config_region is not specified, will default
        to 'swarm', or the local project-specific config
        file.
        """
        if config_region in self._config['regions']:
            self._config[config_region].set(section, setting, value)
        else:
            # Default is to swarm
            self._config[self._config['regions'][-1]].set(section, setting, value)

    def add_section(self, section, config_region=None):
        """
        Add a new section to a config file
        section = The section title to add
        config_region = The config region to look up

        config_region can be one of 'system' (or system-
        wide settings), 'user' (or user-specific settings),
        or 'swarm' (project-specific settings).

        If config_region is not specified, will default
        to 'swarm', or the local project-specific config
        file.
        """
        if config_region in self._config['regions']:
            self._config[config_region].add_section(section)
        else:
            # Default is to last entry (swarm)
            self._config[self._config['regions'][-1]].add_section(section)

    def has_section(self, section, config_region=None):
        """
        Returns true if a section exists
        """
        if config_region in self._config['regions']:
            return self._config[config_region].has_section(section)
        else:
            return self._config[self._config['regions'][-1]].has_section(section)

    def save(self):
        """
        Save the project's swarmrc file.

        Will save the project-specific swarm config
        file.

        This probably should be made more generally,
        however, right now I'm not convinced we should
        even be setting/saving none project swarmrc
        files. Then again, we allow it above...
        so who the fuck knows? Let's decide and fix it
        later....
        - Sam 2007-06-21
        """
        self._logger.register("save")
        swarm_config = "%s/swarmrc" % self.dot_swarm

        self._logger.entry("Attempting to create swarm rc '%s'" % swarm_config, 2)

        fp = open(swarm_config, mode="w")
        self._config['swarm'].write(fp)
        fp.close()
        self.config_set = True

        self._logger.unregister()
