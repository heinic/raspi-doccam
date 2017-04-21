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
import socket, json

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
data = ['cam', 'cappic_stream', '']
if (query and query['type'] == 'thumb'): data[2] = 'thumb'
if (query and query['type'] == 'hires'): data[2] = 'hires'
if (query and query['crop']): data[2] += ';' + query['crop']

# IPC
sock = socket.socket()
sock.connect(('127.3.1.4', 3141))
sock.send(json.dumps(data))

# Response
print('Content-type: image/png\n')
try:
    while True:
        imgdata = sock.recv(4096)
        if not imgdata: raise error('')
        sys.stdout.write(imgdata)
        sock.settimeout(1)
except Exception as e:
    pass
sock.close()
