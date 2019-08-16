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
import os
import requests
import time
import getpass
import hashlib
from colorama import init, deinit, Fore, Back, Style

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

        self.set_identity()

        self.requests_headers = {
            'X-auth-token': self.token
        }

        self.post_headers = {
            'X-auth-token': self.token,
            'Content-Type': 'application/json'
        }

        self.calculate_hash()
        self.get_epoch_time()

    def __repr__(self):
        return self.host

    def set_host(self):
        self.host = str(input("--DNA Center host address: "))

    def set_username(self):
        self.username = str(input("--DNA Center API username: "))

    def set_password(self):
        self.password = str(getpass.getpass("--DNA Center API password: "))

    def set_identity(self):
        print('Collecting data for further identification')
        self.params['executer_name'] = str(input("--Your name: "))
        self.params['executer_cco'] = str(input("--Your CCO ID: "))

    def calculate_hash(self):
        try:
            with open('dnacbackend.py', 'rb') as file:
                contents = file.read()
                self.params['sha256'] = hashlib.sha256(contents).hexdigest()
        except FileNotFoundError:
            self.params['sha256'] = 'ERROR: could not calculate hash - file not found'

    def get_epoch_time(self):
        self.epoch_time = int(time.time())*1000

    def ask_for_permision(message):
        """Decision decorator, askes for confirmation before running an API function"""
        def _decorator(function):
            def wrapper(self):
                if self.config['ask_for_permission']:
                    opt_yes = ['y', 'yes']
                    opt_no = ['n', 'no']
                    print(message)
                    while True:
                        print("Please use {tfyes}[{yes}]{tfreset} for 'yes' or {tfno}[{no}]{tfreset} for 'no'. [default {tfyes}'yes'{tfreset}]".format(
                            yes="/".join(opt_yes),
                            no="/".join(opt_no),
                            tfyes=Fore.GREEN,
                            tfno=Fore.RED,
                            tfreset=Fore.RESET
                        ))
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
        print(Fore.GREEN+"---Creating DNAC profile for {}".format(self.host))
        print(
            "---Running Activation Check on {0}".format(self.host)+Fore.RESET)
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
            print(Fore.RED+"Error processing request"+Fore.RESET, cerror)
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

    def set_executer_in_params(self):
        print('')
        name = input()

    def get_params(self):
        """Retreive collected parameters"""
        return self.params

    def get_hosts(self):
        """Retreive a list of system hosts (wired and wireless)"""
        print(Fore.GREEN+"---Retrieving system hosts"+Fore.RESET)
        r = self._get_url(
            '/api/v1/topology/physical-topology?nodeType=HOST')
        return r.json().get('response')

    @ask_for_permision('--Do you want to count wired and wireless hosts?')
    def count_hosts(self):
        """Counting wired and wireless host/clients"""
        print(Fore.GREEN+"---Counting system hosts"+Fore.RESET)
        hosts = self.get_hosts().get('nodes')
        wired_hosts = [host for host in hosts if host['deviceType'] == 'wired']
        wireless_hosts = [
            host for host in hosts if host['deviceType'] == 'wireless']
        self.params['wired_hosts_count'] = len(wired_hosts)
        self.params['wireless_hosts_count'] = len(wireless_hosts)

        self._count_hosts_via_sitehealt()

    def get_network_devices_inventory(self):
        """Retreive inventory of network devices"""
        print(Fore.GREEN+"---Retrieving network devices inventory list"+Fore.RESET)
        r = self._get_url(
            # '/dna/intent/api/v1/topology/physical-topology?nodeType=device')
            '/api/v1/network-device/')
        return r.json().get('response')

    @ask_for_permision('--Do you wnat to count devices in inventory?')
    def count_network_devices_inventory(self):
        """Count devices in inventory of network devices"""
        print(Fore.GREEN+"---Counting network devices"+Fore.RESET)
        devices_inventory = self.get_network_devices_inventory()
        wlc_count = sum(
            [item['family'] == 'Wireless Controller' for item in devices_inventory])
        ap_count = sum(
            [item['family'] == 'Unified AP' for item in devices_inventory])
        self.params['devices_inventory'] = {
            'inventory_total': len(devices_inventory),
            'wlc_count': wlc_count,
            'ap_count': ap_count,
        }

    def get_fabric_domains_transits(self):
        """Retrieving inventory of fabric domains and transits"""
        print(
            Fore.GREEN+"---Retrieving fabric domains and transits inventory list"+Fore.RESET)
        r = self._get_url(
            '/api/v2/data/customer-facing-service/ConnectivityDomain')
        return r.json().get('response')

    def get_fabric_inventory_by_site(self, site_id):
        """Retrieving fabric devices inventory by site"""
        print(Fore.GREEN+"---Retrieving fabric devices inventory by site"+Fore.RESET)
        r = self._get_url(
            '/api/v2/data/customer-facing-service/DeviceInfo?siteDeviceList={0}'.format(site_id))
        return r.json().get('response')

    def get_fabric_site_poolids(self, siteid):
        """Retrieving fabric pool ids inventory by site"""
        print(Fore.GREEN+"---Retrieving fabric pool ids inventory by site"+Fore.RESET)
        r = self._get_url(
            # '/api/v2/ippool/group?siteId={0}'.format(siteid))
            '/api/v2/ippool?contextvalue={0}'.format(siteid))
        return r.json().get('response')

    @ask_for_permision('--Do you want to count SDA domains?')
    def fabric_domains_transits(self):
        """Fabric domains, transits and vns"""
        print(Fore.GREEN+"---Analyzing fabric and extracting relevant numbers"+Fore.RESET)
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
        print(Fore.GREEN+"---Retrieving fabric devices inventory list"+Fore.RESET)
        r = self._get_url(
            '/api/v2/data/customer-facing-service/DeviceInfo')
        return r.json().get('response')

    @ask_for_permision('--Do you want to collect SDA fabric inventory')
    def fabric_inventory(self):
        """Filtering fabric devices inventory"""
        print(Fore.GREEN+"---Filtering fabric devices inventory list"+Fore.RESET)
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
        print(Fore.GREEN+"---Running Command Runner"+Fore.RESET)
        payload = {"name": "command-runner",
                   "description": "command-runner-network-poller",
                   "deviceUuids": device_uids,
                   "commands": cmds}
        r = self._post_url(
            '/api/v1/network-device-poller/cli/read-request', payload)
        return r.json().get('response')

    def check_task(self, task_id):
        """Checking Command Runner Task ID"""
        print(Fore.GREEN+"---Checking Command Runner Task ID"+Fore.RESET)
        r = self._get_url(
            '/api/v1/task/{0}'.format(task_id))
        return r.json().get('response')

    def check_file(self, file_id):
        """Checking Command Runner File ID"""
        print(Fore.GREEN+"---Checking Command Runner File ID"+Fore.RESET)
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
                print(Fore.YELLOW+"---Task still running. Trying again..."+Fore.RESET)
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
                print(Fore.YELLOW+"---File not ready. Trying again..."+Fore.RESET)
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

    def _get_hosts_via_sitehealth(self):
        payload = {
            "typeList": {
                "type": "SITE",
                "startTime": self.epoch_time - 300000,  # 5 mins
                "endTime": self.epoch_time,
                "timeAPITime": self.epoch_time
            },
            "option": "CLIENT",
            "selectedTypeIdList": [
                "__global__"
            ]
        }
        r = self._post_url(
            '/api/assurance/v1/host/dash/healthdetail', payload=payload)
        return r.json().get('response')

    def _count_hosts_via_sitehealt(self):
        print(Fore.GREEN+"---Counting system hosts via healtcheck"+Fore.RESET)
        sites = self._get_hosts_via_sitehealth()
        for site in sites:
            for item in site['scoreDetail']:
                if item['scoreCategory']['value'] == 'WIRELESS':
                    self.params['wireless_hosts_count_via_healthcheck'] = item['clientUniqueCount']
                if item['scoreCategory']['value'] == 'WIRED':
                    self.params['wired_hosts_count_via_healthcheck'] = item['clientUniqueCount']

    def get_images(self):
        """Retreive a list of software images"""
        print(Fore.GREEN+"---Retrieving software images"+Fore.RESET)
        r = self._get_url(
            '/api/v1/image/importation')
        return r.json().get('response')

    @ask_for_permision('--Do you want to count golden software images?')
    def count_images(self):
        """Counting golden software images"""
        print(Fore.GREEN+"---Counting golden software images"+Fore.RESET)
        images = self.get_images()
        golden_images = [image for image in images if image['isTaggedGolden'] == True]
        self.params['golden_images_count'] = len(golden_images)

    def upgrade_report(self):
        """Command Runner"""
        print(Fore.GREEN+"---Running Upgrade Readiness Report"+Fore.RESET)
        payload = []
        r = self._post_url(
            '/api/v1/image/upgrade-analysis/file', payload)
        return r.json().get('response')

    def download_file(self, file_url):
        """Downloading File URL"""
        print(Fore.GREEN+"---Downloading File URL"+Fore.RESET)
        r = self._get_url(file_url)

        file_name = r.headers['fileName']
        dir_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        file_path = os.path.join(dir_path, file_name)

        with open(file_path, 'wb') as report_file:
            report_file.write(r.content)
        print(Fore.GREEN+"---Downloaded File {0}".format(file_name)+Fore.RESET)

        return file_name

    @ask_for_permision('--Do you want to generate upgrade readiness report?')
    def run_upgrade_report(self):
        """Run report"""
        report = self.upgrade_report()
        task = self.check_task(report['taskId'])

        retries = 12
        while retries > 0:
            try:
                file_id = task["additionalStatusURL"]
                break
            except Exception:
                print(Fore.YELLOW+"---Task still running. Trying again..."+Fore.RESET)
                task = self.check_task(report['taskId'])
                time.sleep(2)
                retries -= 1

        if retries == 0:
            print("Error checking task")
            sys.exit(1)

        retries = 6
        while retries > 0:
            try:
                file = self.download_file(file_id)
                self.params['upgrade_readiness_report'] = file
                return file
            except Exception:
                print(Fore.YELLOW+"---File not ready. Trying again..."+Fore.RESET)
                time.sleep(2)
                retries -= 1

        if retries == 0:
            print("Exception in Downloading File")
            sys.exit(1)

    def get_image_update_status(self):
        """Retreive a list of image update status"""
        print(Fore.GREEN+"---Retrieving image update status"+Fore.RESET)
        r = self._get_url(
            '/api/v1/image/task?taskType=activate')
        return r.json().get('response')

    @ask_for_permision('--Do you want to count image upgrades?')
    def count_image_update_status(self):
        """Counting image upgrades"""
        print(Fore.GREEN+"---Counting image upgrades"+Fore.RESET)
        image_upgrades = self.get_image_update_status()
        upgrades = [image_upgrade for image_upgrade in image_upgrades if image_upgrade['taskStatus'] == "success"]
        self.params['upgrade_images_count'] = len(upgrades)
