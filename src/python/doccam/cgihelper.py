#!/usr/bin/env python
# coding=UTF-8

# Raspberry Pi document camera
# Copyright (C) 2017  Nico Heitmann
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os

def readGetQuery():
    """Read the GET query string supplied by apache2 and seperate it into
    key-value pairs"""

    if not 'QUERY_STRING' in os.environ: return {}

    query = {}
    querystring = os.environ['QUERY_STRING']
    if not os.environ['QUERY_STRING']: return {}

    queryvars = querystring.split('&')
    for queryvar in queryvars:
        varinfo = queryvar.split('=', 1)
        query[varinfo[0]] = varinfo[1]

    return query
