import argparse
import json
import os
import requests

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

w = open('ammo.txt', 'w')

class AmmoMaker:
    token = None
    host = None
    port = None
    get_requests_uri = {
        'service': '', 'workflow': '', 'scenario': '', 'kladr':'?contentType=city', 'handbook': '/citizenship'
    }

    def __init__(self):
        self.parse_arguments()
        self.headers = {'Authorization': f'token {self.token}', 'Host' : self.host}
        self.session =requests.Session()
        self.session.headers.update(self.headers)

    def parse_arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-t", "--token", type=str, dest="token", help="Authorization token (required)", required=True
        )
        parser.add_argument(
            "-ip", "--host_ip", type=str, dest="host", help="Request host ip (default=127.0.0.1)", default="ebs-dev.iitrust.ru"
        )
        parser.add_argument(
            "-port", "--host_port", type=int, dest="port", help="Request host port (default = 8000)", default=443
        )
        args = parser.parse_args()
        self.token = args.token
        self.host = args.host
        self.port = args.port

    def print_request(self, request):
        headers = ''.join(f'{k}: {v}\r\n' for k, v in request.headers.items())
        if request.body:
            req = f'{request.method} {request.path_url} HTTP/1.1\r\n{headers}\r\n{request.body.decode()}\r\n'
        else:
            req = f'{request.method} {request.path_url} HTTP/1.1\r\n{headers}'

        w.write(f'{len(req)}\n{req}\r\n')

    def make_ammo(self, method, url, body=None, get_service_id = False):
        if body:
            req = requests.Request(method, f'https://{self.host}:{self.port}{url}', headers=self.headers, json=body)
        else:
            req = requests.Request(method, f'https://{self.host}:{self.port}{url}', headers=self.headers)
        prepared = req.prepare()
        if get_service_id:
            service_id = self.session.send(prepared).json()["id"]
            self.make_ammo('GET', f'/api/service/{service_id}')
            self.make_ammo('PUT', f'/api/service/{service_id}/draft?is_draft=1', body)
            self.make_ammo('PUT', f'/api/service/{service_id}/draft', body)
        self.print_request(prepared)

    def prepare_requests(self):
        a=True
        for uri, par in self.get_requests_uri.items():
            url = f'/api/{uri}{par}'
            self.make_ammo('GET', url)

        for file_name in os.listdir(DATA_DIR):
            if not a:
                break
            with open(os.path.join(DATA_DIR, file_name)) as f:
                department, vs = file_name.split('.')[0].split('_', maxsplit=1)
                f = json.load(f)
                for service, service_data in f.items():
                    if not a:
                        break
                    url = f'/api/service/{department}/{vs}/{service}'
                    self.make_ammo('POST', f'{url}?is_draft=1', service_data)
                    a=False
        return True

if __name__ == "__main__":
    exit(0) if AmmoMaker().prepare_requests() else exit(1)