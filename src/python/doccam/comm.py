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

import json
import socket

def sendRequest(request):
    """Sends a command to doccam-core and returns the result."""

    sock = socket.socket()
    sock.connect(("127.3.1.4", 3141))

    sock.send(request)
    response = sock.recv(4096)

    sock.close()
    print("IPC: " + request + "; answer: " + response)
    return response

def capturePic(fileob, res=None, crop=None):
    """Capture a picture with doccam-core and save the content to a file object"""
    request = "cam cappic"
    if(res != None): request += " res={res}".format(res=res)
    if(crop != None): request += " crop={crop}".format(
            crop=str.join(",", crop))

    sock = socket.socket()
    sock.connect(('127.3.1.4', 3141))
    sock.send(request)

    try:
        while True:
            imgdata = sock.recv(4096)
            if not imgdata: raise error('')
            fileob.write(imgdata)
            sock.settimeout(1)
    except Exception as e:
        pass
    sock.close()
