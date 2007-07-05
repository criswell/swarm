#!/usr/bin/env python

# time - Swarmlib time module
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

import time

def timestamp(time_tuple=None):
    """
    timestamp(time_tuple=None)
    Returns a floating point timestamp. If on POSIX system, this will
    likely be seconds since epoch.
    If time_tuple is None, will return timestamp for current time.
    """

    if time_tuple:
        return time.mktime(time_tuple)
    else:
        return time.time()