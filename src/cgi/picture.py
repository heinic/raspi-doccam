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

import os, sys
from doccam.comm import capturePic

# POST input
query = {}
query['crop'] = ''
query['type'] = ''

if 'QUERY_STRING' in os.environ:
    querystring = os.environ['QUERY_STRING']
    if querystring:
        queryvars = querystring.split('&')
        for queryvar in queryvars:
            varparts = queryvar.split('=', 1)
            query[varparts[0]] = varparts[1]

# Transfer settings for IPC
extra = ""
if (query and query['type'] == 'thumb'): extra = 'thumb'
if (query and query['type'] == 'hires'): extra = 'hires'
if (query and query['crop']): extra += ';' + query['crop']

# response
print('Content-type: image/png\n')

# capture and send picture
capturePic(sys.stdout, extra=extra)
