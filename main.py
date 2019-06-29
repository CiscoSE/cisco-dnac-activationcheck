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
import json
import time
import os
import sys


def read_json_file(file_url=None):
    with open(file_url, 'r') as json_file:
        return json.loads(json_file.read())


def write_json_file(file_url=None, json_data=None):
    with open(file_url, 'w') as json_file:
        json.dump(json_data, json_file)


if __name__ == "__main__":
    print("---Welcome - Please enter the following information:")

    try:
        connection = DNACSession()

        connection.count_hosts()
        connection.count_network_devices_inventory()
        connection.fabric_domains_transits()
        connection.fabric_inventory()
        # connection.fabric_summary()
        connection.show_commands()

        json_data = connection.get_params()

        file_name_in = "dna-{0}.json".format(time.strftime("%Y%m%d-%H%M%S"))
        file_name_out = "dna-{0}.txt".format(time.strftime("%Y%m%d-%H%M%S"))
        write_json_file(file_name_in, json_data)
        print("---DONE - Data saved in file {0}".format(file_name_in))
    except SystemExit as e:
        print('Press enter to exit...')
        input()
