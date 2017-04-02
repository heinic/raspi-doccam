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
if not 'QUERY_STRING' in os.environ: sys.exit()

querystring = os.environ['QUERY_STRING']
if not querystring: sys.exit()

queryvars = querystring.split('&')
for queryvar in queryvars:
    varparts = queryvar.split('=', 1)
    query[varparts[0]] = varparts[1]


if not query['setting']: sys.exit()
sparts = query['setting'].split('_')
if not len(sparts) == 2: sys.exit()

if not 'value' in query: query['value'] = ''

# IPC
sobject = (sparts[0], sparts[1], query['value'])
datastring = json.dumps(sobject)

sock = socket.socket()
sock.connect(("127.3.1.4", 3141))
sock.send(datastring)

# Response
print('Content-type: text/plain\n')
sys.stdout.write(sock.recv(4096))
sock.close()
