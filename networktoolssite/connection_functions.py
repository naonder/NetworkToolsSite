#!/usr/bin/env python3

import yaml
import ipaddress
from nornir import InitNornir
from nornir.plugins.tasks import networking
from nornir.plugins.functions.text import print_result


class ConnectionMethods(object):  # Left it as a class just because
    def __init__(self):
        self.host_file = 'networktoolssite/hosts.yaml'
        self.defaults_file = 'networktoolssite/defaults.yaml'
        self.group_file = 'networktoolssite/groups.yaml'

    def base_settings(self, network_device):  # Set up the Nornir object and attributes
        nr = InitNornir(core={"num_workers": 100},
                        inventory={"plugin": "nornir.plugins.inventory.simple.SimpleInventory",
                                   "options": {"host_file": self.host_file,
                                               "defaults_file": self.defaults_file,
                                               "group_file": self.group_file}})
        device = nr.filter(name=network_device)
        return device

    def get_l2_devices(self):  # Will return a list of all switches
        with open('networktoolssite/hosts.yaml', 'r') as hosts:
            dict_devices = yaml.safe_load(hosts)
            all_devices = [device for device, values in dict_devices.items()
                           if values.get('groups', None)
                           if 'l2_devices_ios' in values.get('groups') or 'l2_devices_nxos' in values.get('groups')]
            sorted_devices = [switch for switch in all_devices]
        return sorted_devices

    def get_arp_devices(self):  # Returns only layer3 devices from the hosts.yaml file
        with open('networktoolssite/hosts.yaml', 'r') as hosts:
            dict_devices = yaml.safe_load(hosts)
            l3_devices = [device for device, values in dict_devices.items()
                          if values.get('groups', None)
                          if 'l3_devices_ios' in values.get('groups') or 'l3_devices_nxos' in values.get('groups')]
            sorted_devices = [device for device in l3_devices]
        return sorted_devices

    def get_interfaces(self, device, network_device):  # Returns a list of interfaces if the connection succeeds
        result = device.run(task=networking.napalm_get, getters=['get_facts'])
        full_entry = result[network_device][0].__dict__  # Converts result into a dictionary object
        entries = full_entry['result']['get_facts']['interface_list']
        skips = ['Port', 'Loopback', 'Vlan', 'mgmt', 'port', 'loopback']
        all_interfaces = []
        for entry in entries:
            if not any(x in entry for x in skips):
                all_interfaces.append(entry)
        if result.failed:  # If connection fails, return True and let client know
            return result.get(network_device).exception, True
        else:
            return all_interfaces, False

    def get_port_configuration(self, device, interface):  # Simple show run of an interface
        result = device.run(task=networking.netmiko_send_command,
                            command_string='show run interface {}'.format(interface))
        running_config = '\n'.join([running_config.result for running_config in result.values()])
        return running_config

    def set_description(self, device, interface, description):  # Sets a description on an interface
        device.run(task=networking.netmiko_send_config, config_commands=['interface {}'.format(interface),
                                                                         'description {}'.format(description)])

    def get_vlans(self, device):  # Will grab most VLANs from a device
        result = device.run(task=networking.netmiko_send_command, command_string='sh vlan br | e Name|Status|Ports|---')

        vlans = '\n'.join([vlan.result for vlan in result.values()])
        no_go_vlans = ['1002', '1003', '1004', '1005', 'Fa', 'Gi', 'Te', 'Po']
        all_vlans = []
        for line in vlans.splitlines():
            try:
                vlan_id, vlan_name = line.split()[0], line.split()[1]
                if not any(word in vlan_id for word in no_go_vlans):
                    all_vlans.append(vlan_id + ' - ' + vlan_name)
            except IndexError:
                pass

        return all_vlans

    def check_cdp_neighbor(self, device, interface):  # Verifies a neighbor isn't another switch, router, or AP
        result = device.run(task=networking.netmiko_send_command,
                            command_string='show cdp neighbors {} detail'.format(interface))

        neighbors = '\n'.join([neighbors.result for neighbors in result.values()])

        if neighbors:

            neighbor_entries = neighbors.split('------')

            neighbor_list = []
            for neighbor in neighbor_entries:
                if neighbor != '':
                    details = {}
                    for line in neighbor.splitlines():
                        if 'Device ID' in line:
                            details['name'] = line.split(' ')[-1]
                        if 'Platform' in line:
                            details['capabilities'] = line.split(' ')[4:]
                else:
                    continue
                neighbor_list.append(details)

            checks = ['Router', 'Switch', 'IGMP']
            return_neighbors = []
            for neighbor in neighbor_list:
                if any(word in checks for word in neighbor.get('capabilities')):
                    return_neighbors.append(neighbor)
            return return_neighbors

    def push_configuration(self, device, interface, config):  # Will default an interface
        result = device.run(task=networking.netmiko_send_config,
                            config_commands=['default interface {}'.format(interface) + '\n', config])
        print_result(result)

    def clear_sticky_mac(self, device, address):  # Will clear a sticky MAC
        result = device.run(task=networking.netmiko_send_command,
                            command_string='clear port-security sticky address {}'.format(address))
        print_result(result)

    def clear_sticky_interface(self, device, interface):  # Will clear sticky MACs from an interface
        result = device.run(task=networking.netmiko_send_command,
                            command_string='clear port-security sticky interface {}'.format(interface))
        print_result(result)

    def check_arp(self, device, l3_device, address):  # Attempts to show ARP mapping for either IP or MAC address
        result = device.run(task=networking.napalm_get, getters=['arp_table'])

        full_entry = result[l3_device][0].__dict__  # Convert result for device getter into a dictionary object

        entries = full_entry['result']['arp_table']  # Entries is a list of dictionaries of interface, address, mac
        for entry in entries:
            for k, v in entry.items():
                if str(v) == address:
                    if k == 'ip':
                        return f"{address} maps to {entry['mac']}"
                    elif k == 'mac':
                        return f"{address} maps to {entry['ip']}"
        return 'No mapping found for {}. Check that device is online, address was correctly entered, ' \
               'and search is from correct device.'.format(address)

    def validate_format_mac(self, mac_address):  # Validates entered address is a valid MAC address
        dividers = '.-: '
        try:
            new_mac = ''.join(c for c in mac_address if c not in dividers)
            int(new_mac, 16)  # is MAC address hex?
            if len(new_mac) != 12:  # is MAC address (minus dividers) at least 12 chars long
                return False
        except ValueError:
            return False

        formatted_mac = new_mac.lower()[0:4] + '.' + new_mac.lower()[4:8] + '.' + new_mac.lower()[8:]
        return formatted_mac

    def validate_ip_address(self, ip_address_check):  # Validates entered IP address is valid
        try:
            ipaddress.ip_address(ip_address_check)
        except ValueError:
            return False
        return True


