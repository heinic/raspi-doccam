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
from doccam.cgihelper import readGetQuery

# POST input
query = readGetQuery()

# Transfer settings for IPC
extra = {}
if ('res' in query): extra["res"] = query["res"]
if ('crop' in query): extra["crop"] = query['crop'].split(",")

# response
print('Content-type: image/png\n')

# capture and send picture
capturePic(sys.stdout, **extra)
