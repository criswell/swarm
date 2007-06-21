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
import sys
import time

class log:
    def __init__(self, universal_loglevel=0):
        self._universal_loglevel = universal_loglevel
        self._logstart()
        self._out = sys.stdout
        self._mylogger = self._logger("log")

    def _logstart(self):
        """ In the future, we will likely want to put in other
            logging functionality here, but for now, this just
            prints information based on the log level """

        if self._universal_loglevel > 5:
            self._mylogger.entry("_logstart", "Starting log...", 5)

    def get_logger(self, module_name="Unkown", loglevel=None):
        if not loglevel:
            loglevel = self._universal_loglevel
        return self._logger(module_name, loglevel, self._out)

    def set_universal_loglevel(self, universal_loglevel=0):
        self._universal_loglevel = universal_loglevel

    class _logger:
        def __init__(self, module_name="Unknown", loglevel=0, output=sys.stdout, error=sys.stderr):
            self._module_name = module_name
            self._default_entry = "Unknown! This should not happen! Something called internal log.entry() without an actual entry!"
            self._function_name = []
            self._out = output
            self._error = error
            self._loglevel = loglevel

        def entry(self, entry=None, loglevel=1):
            if loglevel <= self._loglevel:
                if not entry:
                    entry = self._default_entry

                if len(self._function_name):
                    function_name = self._function_name[-1]
                else:
                    function_name = "Unknown"

                self._logentry(self._out, function_name, entry)

        def error(self, entry=None):
            if len(self._function_name):
                function_name = self._function_name[-1]
            else:
                function_name = "Unknown"

            self._logentry(self._error, function_name, entry)

        def _logentry(self, output, function_name, entry):
            curtime = time.strftime("%Y %b %d %H:%M.%S", time.localtime(time.time()))
            outpur.write("%s [%s.%s] : %s\n" % (curtime, self._module_name, function_name, entry))

        def register(self, function_name=None):
            if function_name:
                self._function_name.append(function_name)

        def unregister(self):
            if len(self._function_name):
                self._function_name.pop()
            # Silently fails if function_name stack is empty,
            # may not be the best behavior
