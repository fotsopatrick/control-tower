#!/usr/bin/env python3
import sys
import json
import urllib.request

# Bridge stdio to HTTP Router
def bridge():
    for line in sys.stdin:
        try:
            request = json.loads(line)
            # Forward to HTTP router
            req = urllib.request.Request(
                'http://localhost:8080',
                data=json.dumps(request).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req) as response:
                result = response.read().decode('utf-8')
                sys.stdout.write(result + '\n')
                sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(str(e) + '\n')
            sys.stderr.flush()

if __name__ == "__main__":
    bridge()
