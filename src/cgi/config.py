#!/usr/bin/env python
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
