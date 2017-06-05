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
import sys


def get_pia_connections(region):
    if region == 'us':
        search_term = 'PIA - US'
    else:
        search_term = 'PIA - '
    sys_cons = '/etc/NetworkManager/system-connections/'
    if region == 'int':
        return [i for i in os.listdir(sys_cons) if (search_term in i) & ('US' not in i)]
    else:
        return [i for i in os.listdir(sys_cons) if search_term in i]


def pick_rand_con(cons):
    return cons[randint(0, len(cons))]


def make_connection(con):
    print('Activating {}...'.format(con))
    subprocess.call(['nmcli', 'con', 'up', 'id', con])


def connect_vpn(region):
    cons = get_pia_connections(region)
    con = pick_rand_con(cons)
    make_connection(con)


def disconnect_vpn():
    active_cons = subprocess.check_output(['nmcli', 'con', 'show', '--active']).decode('utf-8')
    vpns = []
    for i in active_cons.split('\n'):
        if re.search('\svpn\s', i):
            vpns.append(re.split('\s+\S{36}\s+', i)[0])
    for i in vpns:
        print('Disconnecting {}...'.format(i))
        subprocess.call(['nmcli', 'con', 'down', 'id', i])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--region', choices=['us', 'all', 'int'],
                        help='"us" for US only, "int" for non-US, "all" for worldwide')
    parser.add_argument('-d', '--disconnect', action='store_true',
                        help='disconnect current PIA vpn connection')
    args = parser.parse_args()
    if not args.region:
        region = 'us'
    else:
        region = args.region

    if args.disconnect:
        disconnect_vpn()
    else:
        disconnect_vpn()
        connect_vpn(region)
