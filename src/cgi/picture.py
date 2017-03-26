#!/usr/bin/env python
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
        sock.settimeout(0.5)
except Exception as e:
    pass
sock.close()
