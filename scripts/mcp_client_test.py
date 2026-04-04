#!/usr/bin/env python3
import subprocess
import json
import sys
import threading

# Start the awesome-copilot container as a stdio process
cmd = [
    'docker','run','-i','--rm','ghcr.io/microsoft/mcp-dotnet-samples/awesome-copilot:latest'
]
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Function to read one JSON-RPC message from stdout (Content-Length framing)
def read_message(stdout):
    # Read headers
    headers = b""
    while True:
        line = stdout.readline()
        if not line:
            return None
        headers += line
        if headers.endswith(b"\r\n\r\n"):
            break
    # parse headers for content-length
    headers_text = headers.decode('utf-8', errors='ignore')
    length = 0
    for h in headers_text.split('\r\n'):
        if h.lower().startswith('content-length:'):
            length = int(h.split(':',1)[1].strip())
    if length==0:
        return None
    body = stdout.read(length)
    return body.decode('utf-8', errors='ignore')

# Function to send request
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

# read response
resp = read_message(proc.stdout)
if resp is None:
    # attempt to read stderr for clues
    stderr = proc.stderr.read().decode('utf-8', errors='ignore')
    print('No response on stdout. stderr:')
    print(stderr)
    proc.kill()
    sys.exit(2)

print('Response body:')
print(resp)
proc.kill()
