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
Swarm Hive Connection utilities

Contains various utilities dealing with hive connections
"""

from i18n import _
from swarmlib.exceptions import SchemeNotFoundError
from swarmlib.connect.schemes.local import Local

__scheme_lookup = {
    '' : Local
}

def get_connection(parsed_url, log):
    """
    Given a scheme_classifer (typically, as determined by urlparse), return
    a scheme object which can handle it.
    """

    scheme_classifer = parsed_url.scheme.lower()

    if scheme_classifer in __scheme_lookup.keys():
        return __scheme_lookup[scheme_classifer](parsed_url, config, log)
    else:
        raise SchemeNotFoundError(_("'%s' scheme not defined.") %
                                scheme_classifer)
