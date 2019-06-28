from dnacbackend import DNACSession
import json
import time
import os
import sys
import pyAesCrypt


def read_json_file(file_url=None):
    with open(file_url, 'r') as json_file:
        return json.loads(json_file.read())

def write_json_file(file_url=None, json_data=None):
    with open(file_url, 'w') as json_file:
        json.dump(json_data, json_file)

def encrypt_json_file(action, source, destination):

    # If the input file does not exist, then the program terminates early.
    if not os.path.exists(source):
        print('The file %s does not exist. Quitting...' % (source))
        sys.exit(1)

    # encryption/decryption buffer size - 64K
    bufferSize = 64 * 1024
    password = "ilovesummer"

    if action == 'encrypt':
        pyAesCrypt.encryptFile(source, destination, password, bufferSize)
    elif action == 'decrypt':
        pyAesCrypt.decryptFile(source, destination, password, bufferSize)
    '''
    try:
        os.remove(source)
    except:
        print("---Failed deleting file")
        sys.exit(1)
    '''

if __name__ == "__main__":
    print("---Welcome - Please enter the following information:")

    connection = DNACSession()

    connection.count_hosts()
    connection.count_network_devices_inventory()
    connection.fabric_domains_transits()
    connection.fabric_inventory()
    #connection.fabric_summary()
    connection.show_commands()

    json_data = connection.get_params()

    file_name_in = "dna-{0}.json".format(time.strftime("%Y%m%d-%H%M%S"))
    file_name_out = "dna-{0}.txt".format(time.strftime("%Y%m%d-%H%M%S"))
    write_json_file(file_name_in, json_data)
    encrypt_json_file("encrypt", file_name_in, file_name_out)

    print("---DONE - Data saved in file {0}".format(file_name_out))

    #encrypt_json_file("decrypt", "dna.txt", "dna.json")
    #dict = read_json_file("dna.json")
    #print(dict)
