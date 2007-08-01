#!/usr/bin/env python

# swarmlib - Main swarmlib module
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

class swarm_error(Exception):
    def __init__(self, message, show_traceback=False):
        Exception.__init__(self, message)
        self.message = message
        self.show_traceback = show_traceback

def import_at_runtime(module_name, suite_name):
    """
    Imports a python module determined at runtime.
    """
    try:
        module = __import__(module_name, globals(), locals(), [suite_name])
    except ImportError:
        return None
    return vars(module)[suite_name]

# FIXME : These 'None's should be set to callbacks when we get them
transactions = {
    'xlog_start' : None,
    'set_taxonomy' : None,
    'new_issue' : None,
    'link_issue_to_node' : None,
    'add_lineage' : None,
    'new_node': None,
    'new_issue': None,
}