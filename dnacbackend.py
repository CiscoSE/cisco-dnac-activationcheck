import json
import sys
import requests

requests.packages.urllib3.disable_warnings()


class DNACSession():
    def __init__(self, port=80, host=None, username=None, password=None, token=None,):
        self.host = host if host else self.set_host()
        self.port = port
        print("---Creating DNAC profile for {}".format(self.host))
        if not token:
            self.username = username if username else self.set_username()
            self.password = password if password else self.set_password()
            self.token = self.get_auth_token()
        else:
            self.token = token

        self.requests_headers = {
            'X-auth-token': self.token
        }

        self.params = {}

        self.config = {
            'request_verify': False,
            'show_passwords': False,
            'show_token': False,
            'string_mask': '*'*5,
        }

    def __repr__(self):
        return self.host

    def set_host(self):
        self.host = input("Host address: ")

    def set_username(self):
        self.username = input("Usernamne: ")

    def set_password(self):
        self.password = input("Password: ")

    def set_show_passwords(self, flag=True):
        self.config['show_passwords'] = flag

    def set_show_token(self, flag=True):
        self.config['show_token'] = flag

    def _create_url(self, url):
        host = self.host + ':' + \
            str(self.port) if self.port != 80 else self.host
        return "https://{host}{url}".format(host=host, url=url)

    def _get_url(self, url):
        try:
            url = self._create_url(url)
            print("Sengin get request to {url}".format(url=url))
            return requests.get(url=url, headers=self.requests_headers, verify=self.config['request_verify'])
        except requests.exceptions.RequestException as cerror:
            print("Error processing request", cerror)
            sys.exit(1)

    def _post_url():
        pass

    def get_auth_token(self):
        """Retrieve auth token to be used in futer API calls"""
        login_url = "https://{0}/dna/system/api/v1/auth/token".format(
            self.host, self.port)
        result = requests.post(url=login_url, auth=requests.auth.HTTPBasicAuth(
            self.username, self.password))
        result.raise_for_status()

        token = result.json()["Token"]
        return token

    def get_params(self):
        """Retreive collected parameters"""
        return self.params

    def get_hosts(self):
        """Retreive a list of system hosts (wired and wireless)"""
        print("--Retreiving system hosts")
        r = self._get_url(
            '/dna/intent/api/v1/topology/physical-topology?nodeType=HOST')
        return r.json().get('response')

    def count_hosts(self):
        """Counting wired and wireless host/clients"""
        print("--Counting system hosts")
        hosts = self.get_hosts().get('nodes')
        wired_hosts = [host for host in hosts if host['deviceType'] == 'wired']
        wireless_hosts = [
            host for host in hosts if host['deviceType'] == 'wireless']
        self.params['wired_hosts_count'] = len(wired_hosts)
        self.params['wireless_hosts_count'] = len(wireless_hosts)

    def get_network_devices_inventory(self):
        """Retreive inventory of network devices"""
        print("--Retreiving network devices inventory list")
        r = self._get_url(
            #'/dna/intent/api/v1/topology/physical-topology?nodeType=device')
            '/api/v1/network-device/')
        return r.json().get('response')

    def count_network_devices_inventory(self):
        """Count devices in inventory of network devices"""
        devices_inventory = self.get_network_devices_inventory()
        self.params['devices_inventory'] = len(devices_inventory)
