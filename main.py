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

from dnacbackend import DNACSession
from colorama import init, deinit, Fore, Back, Style
import json
import time
import os
import sys

WELCOME = """

{tf}DNA 'In-Use' Activation software, version 0.1.0
Technical Support: opreda@cisco.com, wrog@cisco.com
Copyright (c) 2019 Cisco and/or its affiliates.
Compiled Thu 18-Jul-19 12:07 by wrog

This scripts is purely read-only (HTTP GET)
except DNA API Token Auth (HTTP POST)

If you require assistance please contact us by sending email to
opreda@cisco.com, wrog@cisco.com.{tfend}
"""

END = """

{tf}Script has finished sucessfully!
Please submit `{extracted_for_validation_json}` file to

    emearsupport-dnac-activation@cisco.com

for validation.

DISCLAIMER
`{extracted_for_validation_json}` does not containg any sensitive data,
only counters, fabric site name and executer name and cco id (for identification purposes).
`{json_data}` shows all parameters that have been collected by the script.
It is generated localy and can be deleted.{tfend}
"""


def read_json_file(file_url=None):
    with open(file_url, 'r') as json_file:
        return json.loads(json_file.read())

def write_json_file(file_name=None, json_data=None):
    dir_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(dir_path, file_name)
    with open(file_path, 'w') as json_file:
        json.dump(json_data, json_file)

def exctract_validation_data(contents):
    result = {}
    #getting direct parameter values
    params = [
        'executer_name',
        'executer_cco',
        'sha256',
        'devices_inventory',
        'wired_hosts_count',
        'wireless_hosts_count',
        'fabric_sites_count',
        ]

    for param in params:
        if param in contents.keys():
            result[param] = contents[param]

    #analyzing SDA fabrics
    result['fabric'] = []
    if 'fabric' in contents.keys():
        for fabric in contents['fabric'].items():
            if fabric[1]['vn_count'] > 0 and fabric[1]['fabric_details']['domainType'] == 'FABRIC_SITE':
                result['fabric'].append({
                    'name': fabric[1]['name'],
                    'vn_count': fabric[1]['vn_count'],
                    'ippool': len(fabric[1]['ippool']),
                    'devices': len(fabric[1]['devices']),
                    'edge': len(fabric[1]['edge']),
                    'control': len(fabric[1]['control']),
                    'border': len(fabric[1]['border']),
                })
                
    return result

if __name__ == "__main__":
    init()
    print(WELCOME.format(tf=Fore.MAGENTA, tfend=Style.RESET_ALL))
    print("-Welcome - Please enter the following information:")

    try:

        connection = DNACSession()
        print(Fore.CYAN+'-Starting case: ASSURANCE'+Fore.RESET)
        connection.count_hosts()
        connection.count_hosts_via_sitehealt()
        connection.count_network_devices_inventory()

        print(Fore.CYAN+'-Starting case: SDA FABRIC'+Fore.RESET)
        connection.fabric_domains_transits()
        connection.fabric_inventory()
        # connection.fabric_summary()
        connection.show_commands()

        json_data = connection.get_params()
        print(Fore.CYAN+'-Extracting data for validation [counters only]'+Fore.RESET)
        extracted_for_validation_json = exctract_validation_data(json_data)

        file_name = "dna-{0}.json".format(time.strftime("%Y%m%d-%H%M%S"))
        write_json_file(file_name, json_data)
        print(Fore.CYAN+"---COLLECTION DONE - Data saved in file {0}".format(file_name)+Fore.RESET)

        file_name_validated = "dna-{0}-extracted.json".format(time.strftime("%Y%m%d-%H%M%S"))
        write_json_file(file_name_validated, extracted_for_validation_json)
        print(Fore.CYAN+"---EXTRACTION DONE - Data saved in file {0}".format(file_name_validated)+Fore.RESET)

        print(END.format(
            extracted_for_validation_json=file_name_validated,
            json_data=file_name,
            tf=Fore.MAGENTA,
            tfend=Style.RESET_ALL
        ))
        print('Press any key to finish')
        deinit()
        input()
    except SystemExit as e:
        print('Press enter to exit...')
        deinit()
