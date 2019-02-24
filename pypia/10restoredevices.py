#!/usr/bin/env python3

import sys
import subprocess
import logging


logging.basicConfig(filename='/tmp/pypia.log', filemode='a', level=logging.DEBUG)
logger = logging.getLogger(__name__)

action = sys.argv[2]
logging.debug(f'action is {action}, iface is {sys.argv[1]}')

if action == "vpn-pre-up":
    logging.debug('loading previously connected devices')
    with open('/tmp/nmcli_connected_devices.conf', 'r') as f:
        logging.debug('restoring device connectivity')
        for i in f.readlines():
            logging.debug(f're-connecting {i}')
            subprocess.call(['nmcli', 'device', 'connect', i])
