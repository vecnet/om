# -*- coding: utf-8 -*-
#
# This file is part of the VecNet OpenMalaria Portal.
# For copyright and licensing information about this package, see the
# NOTICE.txt and LICENSE.txt files in its top-level directory; they are
# available at https://github.com/vecnet/om
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0.  If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

""" This is an implementation of sim_services interface to run OpenMalaria model in a subprocess locally
Tested on Windows, but should work on Linux too.
To be used in development enviroment only as there is no job queueing and server can be easily overloaded
"""

