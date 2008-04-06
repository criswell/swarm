# Copyright 2005-2007 Matt Mackall <mpm@selenic.com>
#
# This software may be used and distributed according to the terms
# of the GNU General Public License, incorporated herein by reference.


"""
i18n.py - internationalization support for Swarm

This file was originally part of Mercurial (which, really is great, you
should check it out if you haven't). Imported and adapted for Swarm by
Sam Hart.
"""

import gettext
t = gettext.translation('swarm', fallback=1)
gettext = t.gettext
_ = gettext
