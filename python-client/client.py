#!/usr/bin/env python

import requests
import json

response = requests.get('https://127.0.0.1:8082/', verify='../certs/ca.crt', cert=('../certs/client.pem', '../certs/client.pem'))

print("Status Code: %s" % response.status_code)
print(json.dumps(response.json(), sort_keys=True, indent=4))
