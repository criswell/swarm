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

from swarmlib.replicate import replicate

class branch:
    def __init__(self, ticket_number, source_sw, dest_sw, log):
        """
        ticket_number == The ticket number we're branching
        source_sw == The source Swarm instance
        dest_sw == The destination Swarm instance
        log == The log instance
        """
        self._ticket_number = ticket_number
        self._source_sw = source_sw
        self._dest_sw = dest_sw
        self._log = log
        self._logger = log.get_logger("branch")
        self._rep = replicate(self._source_sw, self._dest_sw, self._log)

    def run(self):
        """
        Run the branch transaction
        """

        self._logger.register("run")

        # Next, get the transaction log from the source_sw
        # FIXME: This isn't very scalable, we probably should
        # do this in clumps of xaction log entries
        xlog = self._source_sw.get_transaction_log(issue=self._ticket_number)
        self._logger.entry("Processing '%i' transactions" % len(xlog), 0)

        # Now, run through each xaction, and replay it
        # into the dest_sw
        errors = 0
        for (xid, root, time, xaction, xdata) in xlog:
            errors = errors + self._rep.run(xid, root, time, xaction, xdata)

        if errors > 0:
            self._logger.error("There were '%i' errors in the branch transaction" % errors)
            # FIXME
            # We should bail here, probably, since the cloned hive will be in an
            # unknown state
        else:
            # add this clone to tbe upstream tracker
            self._rep.add_tracker(self._ticket_number)
            self._logger.entry("No errors in the branch transaction", 0)

        self._logger.unregister()
