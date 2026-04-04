#!/usr/bin/env python3
import subprocess
import json
import time
import sys

cmd = [
    'docker','run','-i','--rm','ghcr.io/microsoft/mcp-dotnet-samples/awesome-copilot:latest'
]
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

# Wait until server logs indicate ready to read messages
ready = False
start = time.time()
while time.time() - start < 20:
    line = proc.stdout.readline()
    if not line:
        break
    s = line.decode('utf-8', errors='ignore').strip()
    print('[LOG]', s)
    if 'transport reading messages' in s.lower():
        ready = True
        break

if not ready:
    print('Server did not indicate readiness; dumping last 200 chars of stdout')
    rest = proc.stdout.read().decode('utf-8', errors='ignore')
    print(rest[-200:])
    proc.kill()
    sys.exit(2)

# Prepare JSON-RPC request
request = {
    'jsonrpc':'2.0',
    'id':1,
    'method':'mcp_awesome-copil_list_collections',
    'params':{}
}
req_text = json.dumps(request)
req_bytes = req_text.encode('utf-8')
header = f"Content-Length: {len(req_bytes)}\r\n\r\n".encode('utf-8')

# send request
proc.stdin.write(header + req_bytes)
proc.stdin.flush()

# read response framed by Content-Length
# read headers
headers = b''
while True:
    line = proc.stdout.readline()
    if not line:
        print('EOF while reading headers')
        proc.kill()
        sys.exit(3)
    if line.strip()==b'':
        break
    headers += line

# parse content-length
headers_text = headers.decode('utf-8', errors='ignore')
length = 0
for h in headers_text.split('\r\n'):
    if h.lower().startswith('content-length:'):
        try:
            length = int(h.split(':',1)[1].strip())
        except:
            pass

if length==0:
    print('No Content-Length found in headers; printing headers:')
    print(headers_text)
    proc.kill()
    sys.exit(4)

body = proc.stdout.read(length).decode('utf-8', errors='ignore')
print('Response body:')
print(body)
proc.kill()
