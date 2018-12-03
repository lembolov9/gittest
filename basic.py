import json
import os

import requests
from requests import Session

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

s = Session()

def print_request(request):
    headers = ''.join(f'{k}: {v}\r\n' for k,v in request.headers.items())
    if request.body:
        req = f'{request.method} {request.path_url} HTTP/1.1\r\n{headers}\r\n{request.body}'
    else:
        req = f'{request.method} {request.path_url} HTTP/1.1\r\n{headers}'

    return f'{len(req)}\n{req}'

#POST multipart form data
def post_multipart(host, port, namespace, headers, data):
    req = requests.Request(
        'GET',
        'http://{host}:{port}{namespace}'.format(
            host = host,
            port = port,
            namespace = namespace,
        ),
        headers = headers,
        json=data
    )
    prepared = req.prepare()
    return print_request(prepared)

if __name__ == "__main__":
    #usage sample below
    #target's hostname and port
    #this will be resolved to IP for TCP connection
    host = 'ebs-dev.iitrust.ru'
    port = '443'
    namespace = '/api/service/minkomsvyaz/user_order/previous-conviction-status?is_draft=1'
    #below you should specify or able to operate with
    #virtual server name on your target
    headers = {
        'Host': 'ebs-dev.iitrust.ru',
        'Authorization': 'Token 4f6be5cbc41e4ded5f3ce364b078174a9f56fb33'
    }
    with open(os.path.join(DATA_DIR, 'minkomsvyaz_user_order.json')) as f:
        data = json.load(f)['previous-conviction-status']

    print (post_multipart(host, port, namespace, headers, None))