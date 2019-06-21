from dnacbackend import DNACSession
import json

def read_json_file(file_url=None):
    with open(file_url, 'r') as json_file:
        return json.loads(json_file.read())[0]

if __name__ == "__main__":
    hosts_dict = read_json_file("hosts.json")
    for host in hosts_dict['hosts']:
        connection = DNACSession(
            host=host['host'],
            port=host['port'],
            username=host['username'],
            password=host['password'],
            token=host['token'],
        )
        connection.count_hosts()
        connection.count_network_devices_inventory()
        print(connection.get_params())