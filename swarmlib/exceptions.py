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
Swarm Exceptions

All of the possible Swarm-specific exceptions can be found here.
"""

from i18n import _

class _SwarmException(Exception):
    post_message = ''
    def __init__(self, message=None):
        if not message:
            Exception.__init__(self,
            _("Unkown error in Swarm code."))
        else:
            Exception.__init__(self, "%s\n%s" % (message, self.post_message))

class SchemeNotFoundError(_SwarmException):
    post_message = \
        _("During the connection, the specified scheme could not be found")
    pass
