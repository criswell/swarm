#!/usr/bin/env python

# data_tools - Various tools to manipulate data
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

import marshal
import binascii

def encode_content(content_obj):
    """
    encode_content(content_obj)
    Given some sort of content that is marshalable, will
    encode it into a transportable format
    """
    return binascii.hexlify(marshal.dumps(content_obj))
