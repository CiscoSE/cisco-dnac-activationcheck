#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""activationchecker Console Script.

Copyright (c) 2019 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

"""

__author__ = "Octavian Preda", "Wojciech Rog"
__email__ = "opreda@cisco.com", "wrog@cisco.com"
__version__ = "0.1.0"
__copyright__ = "Copyright (c) 2019 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

import json
import sys
import requests
import time
import getpass

requests.packages.urllib3.disable_warnings()


class DNACSession():
    def __init__(
        self,
        port=80,
        host=None,
        username=None,
        password=None,
        token=None,
    ):
        if host:
            self.host = host
        else:
            self.set_host()

        self.port = port

        self.params = {}

        self.config = {
            'request_verify': False,
            'show_passwords': False,
            'show_token': False,
            'string_mask': '*' * 5,
            'ask_for_permission': True,
        }

        if not token:
            if username:
                self.username = username
            else:
                self.set_username()

            if password:
                self.password = password
            else:
                self.set_password()

            if self.login_ack():
                self.token = self.get_auth_token()
            else:
                sys.exit(1)
        else:
            self.token = token

        self.requests_headers = {
            'X-auth-token': self.token
        }

        self.post_headers = {
            'X-auth-token': self.token,
            'Content-Type': 'application/json'
        }

    def __repr__(self):
        return self.host

    def set_host(self):
        self.host = str(input("--DNA Center host address: "))

    def set_username(self):
        self.username = str(input("--DNA Center API username: "))

    def set_password(self):
        self.password = str(getpass.getpass("--DNA Center API password: "))

    def ask_for_permision(message):
        """Decision decorator, askes for confirmation before running an API function"""
        def _decorator(function):
            def wrapper( self ):
                print(self)
                if self.config['ask_for_permission']:
                    opt_yes = ['y','yes']
                    opt_no = ['n', 'no']
                    print(message)
                    while True:
                        print("Please use [{yes}] for 'yes' or [{no}] for 'no'".format(
                            yes = "/".join(opt_yes),
                            no = "/".join(opt_no),
                        ))
                        print("[deafult 'yes']")
                        decision = input()
                        if decision.lower() in opt_yes or decision == '':
                            function(self)
                            return True
                        elif decision.lower() in opt_no:
                            return False
                        print("Decision unknown!")
            return wrapper
        return _decorator

    @ask_for_permision('--Login data complete, do you want to continue with activation check?')
    def login_ack(self):
        print("---Creating DNAC profile for {}".format(self.host))
        print("---Running Activation Check on {0}".format(self.host))
        return True

    def set_show_passwords(self, flag=True):
        self.config['show_passwords'] = flag

    def set_show_token(self, flag=True):
        self.config['show_token'] = flag

    def set_ask_for_permission(self, flag=True):
        self.config[ask_for_permission] = flag

    def _create_url(self, url):
        host = self.host + ':' + \
            str(self.port) if self.port != 80 else self.host
        return "https://{host}{url}".format(host=host, url=url)

    def _get_url(self, url):
        # TO DO HTTP error handling
        try:
            url = self._create_url(url)
            #print("Sending get request to {url}".format(url=url))
            r = requests.get(
                url=url,
                headers=self.requests_headers,
                verify=self.config['request_verify'])
            if r.status_code == 200 or r.status_code == 204:
                return r
            else:
                print("Error bad response", r.status_code, r.text)
                sys.exit(1)
        except requests.exceptions.RequestException as cerror:
            print("Error processing request", cerror)
            sys.exit(1)

    def _post_url(self, url, payload):
        # TO DO HTTP error handling
        try:
            url = self._create_url(url)
            #print("Sending get request to {url}".format(url=url))
            payload = json.dumps(payload)
            return requests.post(
                url=url,
                headers=self.post_headers,
                data=payload,
                verify=self.config['request_verify'])
        except requests.exceptions.RequestException as cerror:
            print("Error processing request", cerror)
            sys.exit(1)

    def get_auth_token(self):
        """Retrieve auth token to be used in futer API calls"""
        # login_url = "https://{0}/dna/system/api/v1/auth/token".format(
        login_url = "https://{0}/api/system/v1/auth/token".format(
            self.host, self.port)
        try:
            result = requests.post(
                url=login_url, auth=requests.auth.HTTPBasicAuth(
                    self.username, self.password), verify=False)
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Http Error: ", err)
            sys.exit(1)
        except requests.exceptions.ConnectionError as err:
            print("Error Connecting: ", err)
            sys.exit(1)
        except requests.exceptions.Timeout as err:
            print("Timeout Error: ", err)
            sys.exit(1)
        except requests.exceptions.RequestException as err:
            print("Oops: Something went wrong: ", err)
            sys.exit(1)

        token = result.json()["Token"]
        return token

    def get_params(self):
        """Retreive collected parameters"""
        return self.params

    def get_hosts(self):
        """Retreive a list of system hosts (wired and wireless)"""
        print("---Retrieving system hosts")
        r = self._get_url(
            '/api/v1/topology/physical-topology?nodeType=HOST')
        return r.json().get('response')

    @ask_for_permision('--Do you want to count wired and wireless hosts?')
    def count_hosts(self):
        """Counting wired and wireless host/clients"""
        print("---Counting system hosts")
        hosts = self.get_hosts().get('nodes')
        wired_hosts = [host for host in hosts if host['deviceType'] == 'wired']
        wireless_hosts = [
            host for host in hosts if host['deviceType'] == 'wireless']
        self.params['wired_hosts_count'] = len(wired_hosts)
        self.params['wireless_hosts_count'] = len(wireless_hosts)

    
    def get_network_devices_inventory(self):
        """Retreive inventory of network devices"""
        print("---Retrieving network devices inventory list")
        r = self._get_url(
            # '/dna/intent/api/v1/topology/physical-topology?nodeType=device')
            '/api/v1/network-device/')
        return r.json().get('response')

    @ask_for_permision('--Do you wnat to count devices in inventory?')
    def count_network_devices_inventory(self):
        """Count devices in inventory of network devices"""
        print("---Counting network devices")
        devices_inventory = self.get_network_devices_inventory()
        self.params['devices_inventory'] = len(devices_inventory)

    def get_fabric_domains_transits(self):
        """Retrieving inventory of fabric domains and transits"""
        print("---Retrieving fabric domains and transits inventory list")
        r = self._get_url(
            '/api/v2/data/customer-facing-service/ConnectivityDomain')
        return r.json().get('response')

    def get_fabric_inventory_by_site(self, site_id):
        """Retrieving fabric devices inventory by site"""
        print("---Retrieving fabric devices inventory by site")
        r = self._get_url(
            '/api/v2/data/customer-facing-service/DeviceInfo?siteDeviceList={0}'.format(site_id))
        return r.json().get('response')

    def get_fabric_site_poolids(self, siteid):
        """Retrieving fabric pool ids inventory by site"""
        print("---Retrieving fabric pool ids inventory by site")
        r = self._get_url(
            # '/api/v2/ippool/group?siteId={0}'.format(siteid))
            '/api/v2/ippool?contextvalue={0}'.format(siteid))
        return r.json().get('response')

    @ask_for_permision('--Do you want to count SDA domains?')
    def fabric_domains_transits(self):
        """Fabric domains, transits and vns"""
        print("---Analyzing fabric and extracting relevant numbers")
        fabric_domains_transits = self.get_fabric_domains_transits()
        self.params['fabric_lans_count'] = sum(
            1 for item in fabric_domains_transits if item["domainType"] == "FABRIC_LAN")
        self.params['fabric_sites_count'] = sum(
            1 for item in fabric_domains_transits if item["domainType"] == "FABRIC_SITE")
        self.params['transits_count'] = sum(
            1 for item in fabric_domains_transits if item["domainType"] == "TRANSIT")

        self.params['fabric'] = {}

        for item in fabric_domains_transits:
            item_id = item["id"]
            self.params['fabric'][item_id] = {}
            self.params['fabric'][item_id]["vn_count"] = len(
                item["virtualNetwork"])
            self.params['fabric'][item_id]["name"] = item["name"]
            self.params['fabric'][item_id]["fabric_details"] = item

            """Gather fabric site ip pool"""
            if "siteId" in self.params['fabric'][item_id]["fabric_details"]:
                ip_pools = self.get_fabric_site_poolids(
                    self.params['fabric'][item_id]["fabric_details"]["siteId"])
                self.params['fabric'][item["id"]]["ippool"] = ip_pools

            """Gather fabric devices inventory"""
            self.params['fabric'][item_id]["devices"] = []
            self.params['fabric'][item_id]["edge"] = []
            self.params['fabric'][item_id]["control"] = []
            self.params['fabric'][item_id]["border"] = []
            #self.params['fabric'][item_id]["device_details"] = []

            if "siteId" in self.params['fabric'][item["id"]]["fabric_details"]:
                fabric_by_site = self.get_fabric_inventory_by_site(
                    self.params['fabric'][item_id]["fabric_details"]["siteId"])
                for item_site in fabric_by_site:
                    if "roles" in item_site:
                        if "EDGENODE" in item_site["roles"]:
                            self.params['fabric'][item_id]["edge"].append(
                                item_site["networkDeviceId"])
                            self.params['fabric'][item_id]["devices"].append(
                                item_site["networkDeviceId"])
                            # self.params['fabric'][item_id]["device_details"].append(item_site)
                        if "MAPSERVER" in item_site["roles"]:
                            self.params['fabric'][item_id]["control"].append(
                                item_site["networkDeviceId"])
                            self.params['fabric'][item_id]["devices"].append(
                                item_site["networkDeviceId"])
                            # self.params['fabric'][item_id]["device_details"].append(item_site)
                        if "BORDERNODE" in item_site["roles"]:
                            self.params['fabric'][item_id]["border"].append(
                                item_site["networkDeviceId"])
                            self.params['fabric'][item_id]["devices"].append(
                                item_site["networkDeviceId"])
                            # self.params['fabric'][item_id]["device_details"].append(item_site)

    def fabric_summary(self):
        for item in self.params['fabric']:
            self.params['fabric'][item]["ip_pool_count"] = 0
            self.params['fabric'][item]["edge_count"] = 0
            self.params['fabric'][item]["control_count"] = 0
            self.params['fabric'][item]["border_count"] = 0

            if "ippool" in self.params['fabric'][item]:
                self.params['fabric'][item]["ip_pool_count"] = len(
                    self.params['fabric'][item]["ippool"])
            if "edge" in self.params['fabric'][item]:
                self.params['fabric'][item]["edge_count"] = len(
                    self.params['fabric'][item]["edge"])
            if "control" in self.params['fabric'][item]:
                self.params['fabric'][item]["control_count"] = len(
                    self.params['fabric'][item]["control"])
            if "border" in self.params['fabric'][item]:
                self.params['fabric'][item]["border_count"] = len(
                    self.params['fabric'][item]["border"])

    def get_fabric_inventory(self):
        """Retrieving fabric devices inventory"""
        print("---Retrieving fabric devices inventory list")
        r = self._get_url(
            '/api/v2/data/customer-facing-service/DeviceInfo')
        return r.json().get('response')

    @ask_for_permision('--Do you want to collect SDA fabric inventory')
    def fabric_inventory(self):
        """Filtering fabric devices inventory"""
        print("---Filtering fabric devices inventory list")
        self.params["global_fabric_devices"] = []
        self.params["global_fabric_edge"] = []
        self.params["global_fabric_control"] = []
        self.params["global_fabric_border"] = []
        #self.params["fabric_devices_details"] = []
        fabric_devices_inventory = self.get_fabric_inventory()
        for item in fabric_devices_inventory:
            if "roles" in item:
                if "EDGENODE" in item["roles"]:
                    self.params["global_fabric_edge"].append(
                        item["networkDeviceId"])
                    self.params["global_fabric_devices"].append(
                        item["networkDeviceId"])
                    # self.params["fabric_devices_details"].append(item)
                if "MAPSERVER" in item["roles"]:
                    self.params["global_fabric_control"].append(
                        item["networkDeviceId"])
                    self.params["global_fabric_devices"].append(
                        item["networkDeviceId"])
                    # self.params["fabric_devices_details"].append(item)
                if "BORDERNODE" in item["roles"]:
                    self.params["global_fabric_border"].append(
                        item["networkDeviceId"])
                    self.params["global_fabric_devices"].append(
                        item["networkDeviceId"])
                    # self.params["fabric_devices_details"].append(item)

    def command_runner(self, device_uids, cmds):
        """Command Runner"""
        print("---Running Command Runner")
        payload = {"name": "command-runner",
                   "description": "command-runner-network-poller",
                   "deviceUuids": device_uids,
                   "commands": cmds}
        r = self._post_url(
            '/api/v1/network-device-poller/cli/read-request', payload)
        return r.json().get('response')

    def check_task(self, task_id):
        """Checking Command Runner Task ID"""
        print("---Checking Command Runner Task ID")
        r = self._get_url(
            '/api/v1/task/{0}'.format(task_id))
        return r.json().get('response')

    def check_file(self, file_id):
        """Checking Command Runner File ID"""
        print("---Checking Command Runner File ID")
        r = self._get_url(
            '/api/v1/file/{0}'.format(file_id))
        return r.json()

    def run_command(self, devices, cmds):
        """Run Commands using command_runner"""
        command = self.command_runner(devices, cmds)
        task = self.check_task(command['taskId'])

        retries = 12
        while retries > 0:
            try:
                task_progress = json.loads(task["progress"])
                file_id = task_progress["fileId"]
                break
            except Exception:
                print("---Task still running. Trying again...")
                task = self.check_task(command['taskId'])
                time.sleep(2)
                retries -= 1

        if retries == 0:
            print("Error checking task")
            sys.exit(1)

        retries = 6
        while retries > 0:
            try:
                file = self.check_file(file_id)
                return file
            except Exception:
                print("---File not ready. Trying again...")
                time.sleep(2)
                retries -= 1

        if retries == 0:
            print("Exception in Command Runner File Check")
            sys.exit(1)

    @ask_for_permision('--Do you want to execute show commands?')
    def show_commands(self):
        for id, item in self.params["fabric"].items():
            self.params["fabric"][id]["show_commands"] = []
            if item["edge"]:
                cmds = ["show vrf", "show vlan"]
                file = self.run_command(item["edge"], cmds)
                self.params["fabric"][id]["show_commands"].append(file)

            if item["control"]:
                cmds = ["show lisp site summary", "show lisp session"]
                file = self.run_command(item["control"], cmds)
                self.params["fabric"][id]["show_commands"].append(file)
