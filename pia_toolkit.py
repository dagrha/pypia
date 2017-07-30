#!/usr/bin/env python3
"""
Randomly select a Private Internet Access VPN connection.
With command line arguments, you can connect to random US or worldwide
connection, shuffle your connection, or disconnect completely.

Usage:
-----
if script is executable ($ chmod +x random_pia.py):
    ./random_pia.py [-r {us, all, int}] [-d, --disconnect]

otherwise if it's not executable you can do:
    python3 random_pia.py [-r {us, all, int}] [-d, --disconnect]
"""

import os
from random import randint
import subprocess
import re
import argparse
from threading import Thread
from queue import Queue
from pypia import get_vpn_configs


def get_pia_connections(region):
    if region == 'us':
        search_term = 'PIA - US'
    else:
        search_term = 'PIA - '
    sys_cons = '/etc/NetworkManager/system-connections/'
    if region == 'int':
        cons = [i for i in os.listdir(sys_cons) if (search_term in i) & ('US' not in i)]
    else:
        cons = [i for i in os.listdir(sys_cons) if search_term in i]
    return cons


def pick_rand_con(cons):
    return cons[randint(0, len(cons) - 1)]


def make_connection(con):
    print('Activating {}...'.format(con))
    subprocess.call(['nmcli', 'con', 'up', 'id', con])


def connect_vpn(region, disconnected):
    cons = get_pia_connections(region)
    con = pick_rand_con(cons)
    while con in disconnected:
        con = pick_rand_con(cons)
    make_connection(con)


def disconnect_vpn():
    active_cons = subprocess.check_output(['nmcli', 'con', 'show', '--active']).decode('utf-8')
    active_pia = []
    for i in active_cons.split('\n'):
        if re.search('\svpn\s', i):
            vpn = re.split('\s+\S{36}\s+', i)[0]
            if vpn.startswith('PIA'):
                active_pia.append(vpn)
    for i in active_pia:
        print('Disconnecting {}...'.format(i))
        subprocess.call(['nmcli', 'con', 'down', 'id', i])
    return active_pia


class Latencies():

    def __init__(self, region):
        self.configs = get_vpn_configs()
        self.q = Queue()
        self.latencies = {}
        self.get_ip_addresses(region)
        print('Pinging all PIA servers. This might take a few seconds...\n')
        self.threaded_pings()
        self.get_fastest()

    def get_ip_addresses(self, region):
        cons = [i.split(' - ')[-1] for i in get_pia_connections(region)]
        self.ip_addresses = {}
        for k in self.configs:
            if isinstance(self.configs[k], dict):
                if self.configs[k].get('ping'):
                    if self.configs[k]['name'] in cons:
                        ip = self.configs[k]['ping'].split(':')[0]
                        self.ip_addresses[ip] = self.configs[k]['name']
                        self.q.put(ip)

    def ping(self):
        ip = self.q.get()
        result = subprocess.check_output(['ping', '-c', '3', ip]).decode('utf-8')
        avg = float(result.split('=')[-1].split('/')[1])
        self.latencies[ip] = avg
        self.q.task_done()

    def threaded_pings(self):
        for i in range(len(self.q.queue)):
            worker = Thread(target=self.ping)
            worker.start()
        self.q.join()

    def get_fastest(self):
        fastest = min(self.latencies, key=self.latencies.get)
        self.fastest = 'PIA - ' + self.ip_addresses[fastest]

    def __repr__(self):
        return str(self.latencies)

    def __str__(self):
        table = ' {:<20} {:<17} {:>11} \n'.format('name', 'ip', 'ping (ms)')
        table += '-' * 52 + '\n'
        for k in sorted(self.latencies, key=self.latencies.get):
            table += '| {:<18} | {:<15} | {:>9.2f} |\n'.format(self.ip_addresses[k],
                                                               k, self.latencies[k])
        return table


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Connection tools for PIA VPNs.')
    parser.add_argument('-p', '--ping', action='store_true',
                        help='ping each vpn server and list latencies')
    parser.add_argument('-s', '--shuffle', action='store_true',
                        help='connect to or shuffle a random vpn')
    parser.add_argument('-r', '--region', choices=['us', 'all', 'int'],
                        help='"us" for US only, "int" for non-US, "all" for worldwide')
    parser.add_argument('-f', '--fastest', action='store_true',
                        help='connect to network with lowest ping latency')
    parser.add_argument('-d', '--disconnect', action='store_true',
                        help='disconnect current PIA vpn connection')
    args = parser.parse_args()
    if not any(vars(args).values()):
        parser.print_help()
        parser.exit(1)
    if not args.region:
        region = 'us'
    else:
        region = args.region
    if args.disconnect:
        disconnect_vpn()
    if args.fastest:
        disconnect_vpn()
        lat = Latencies(region)
        print(lat)
        make_connection(lat.fastest)
    elif args.ping:
        lat = Latencies(region)
        print(lat)
    if args.shuffle:
        disconnected = disconnect_vpn()
        connect_vpn(region, disconnected)
