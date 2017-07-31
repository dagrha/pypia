# -*- coding: utf-8 -*-
"""
This script facilitates the configuration of Private Internet Access (PIA)
(https://www.privateinternetaccess.com/) Virtual Private Network (VPN) routes
on various linux distributions. The script detects the operating system,
installs required packages, downloads the PIA certificate, downloads VPN
server information, automatically creates openvpn configuration files to be
used by Network Manager, and restarts Network Manager.

Upon completion of the script, PIA VPN routes are accessible via the Network
Manager Applet, or via `nmcli`.

This is a Python 3 script and will not work with Python 2. Root priveleges
are needed to write configuration files to `/etc/` and to restart the Network
Manager daemon.

Usage
-----
    sudo python3 pypia.py

"""

import sys
import os
import subprocess
import getpass
import uuid
import json
from random import randint
import re
import argparse
from threading import Thread
from queue import Queue
try:
    import urllib.request
except ImportError:
    sys.exit("Sorry, this script requires python 3.x")


def verify_running_as_root():
    """
    Check that user has root priveleges.

    This script will write configuration files to `/etc/` so root priveleges
    are required. If priveleges are insufficient, script will exit.

    """
    if os.getuid() != 0:
        sys.exit('Script must be run as root in order to write config ' +
                 'files to /etc/ and to restart the network manager service' +
                 ' upon completion. Exiting.\n')


class Distro():

    def __init__(self):
        self.get_distro()
        self.get_package_info()

    def get_package_info(self):
        with open('./pypia/package_info.json', 'r') as package_info:
            package_dict = json.load(package_info)
        self.required_packages = package_dict['required_packages'][self.distro]
        self.install_command = package_dict['install_commands'][self.distro]

    def get_distro(self):
        """
        Get the name of the Linux distribution this script is being run on.

        Returns
        -------
        distro : str
            Short name for operating system listed in `/etc/os-release`
        """
        os_release = subprocess.check_output(['cat', '/etc/os-release']) \
            .decode('utf-8').splitlines()
        self.os_dict = {i.split('=')[0]: i.split('=')[1].strip('"')
                   for i in os_release if '=' in i}
        self.distro = self.os_dict['ID'].lower()

    def install_packages(self):
        """
        Install packages required for Private Internet Access to be accessible
        from the Network Manager applet. You may be prompted twice about
        installing required packages: once by this script and once by the package
        manager. If you say 'yes' this script's prompt and 'no' at the package
        manager's prompt, the script will continue and appear to complete
        successfully. But `openvpn` may not have been installed and trying to
        connect to the PIA routes will fail.

        Parameters
        ----------
        package_dict : dict
            Dictionary with required packages (as lists) and installation commands
            (as strings) for each supported distribution.

        """
        for package in self.required_packages:
            raw = input('Installing {}. OK? (y/n): '.format(package))
            if (raw.lower() == 'y') | (raw.lower() == 'yes'):
                os.system(self.install_command.format(package))
            else:
                sys.exit('\n{} required. Exiting.\n'.format(package))


    def restart_network_manager(self):
        """
        Use `systemctl` (systemd) command to restart the Network Manager service.

        Notes
        -----
            This will not work on systems without systemd.

        """
        print('Restarting network manager...')
        os.system('systemctl restart NetworkManager.service')


class PiaConfigurations():

    def __init__(self):
        self.cert_address = 'https://www.privateinternetaccess.com/openvpn/ca.rsa.2048.crt'
        self.config_address = 'https://privateinternetaccess.com/vpninfo/servers'
        self.config_dir = '/etc/NetworkManager/system-connections/'
        self.get_vpn_configs()

    def get_credentials(self):
        """
        Request Private Internet Access user credentials.

        The credentials are stored in the VPN configuration files in
        `/etc/NetworkManager/system-connections/`.

        Returns
        -------
        username : str
            The user's Private Internet Access username
        password : str
            The user's Private Internet Access password

        """
        self.username = input('\nEnter your PIA username: ')
        while True:
            self.password = getpass.getpass(prompt='Enter your password: ')
            password2 = getpass.getpass(prompt='Please re-enter password: ')
            if self.password == password2:
                break
            print("\nPasswords do not match. Please try again.")


    def copy_cert(self):
        """
        Download and save Private Internet Access certificate to
        `/etc/openvpn/ca.rsa.2048.crt`.

        An internet connection is needed if cert hasn't already been downloaded.
        If for some reason the cert is not able to be downloaded, or if it hasn't
        previously been downloaded and saved to `/etc/openvpn/ca.rsa.2048.crt`, the script
        will exit.

        """
        try:
            urllib.request.urlretrieve(self.cert_address, '/etc/openvpn/ca.rsa.2048.crt')
            if os.path.exists('/etc/openvpn/ca.rsa.2048.crt'):
                print('PIA certificate downloaded and saved to /etc/openvpn/')
        except (HTTPError, URLError):
            sys.exit('\nPIA cert was not able to be downloaded and saved. ' +
                     'This script needs an internet connection to be able to' +
                     'fetch it automatically. Exiting.\n')

    def get_vpn_configs(self):
        """
        Download json with Private Internet Access server information to be
        parsed and added to Network Manager VPN configuration files.

        An internet connection is needed to download the VPN configuration json.
        If the Private Internet Access server information page is unable to be
        resolved, the script will exit.

        Returns
        -------
        configs_dict : dict
            Dictionary of VPN configuration dictionaries

        """
        try:
            with urllib.request.urlopen(self.config_address) as url:
                config_json = url.read().decode('utf-8').split('\n')[0]
            configs_dict = json.loads(config_json)
            self.configs_dict = {k: v for k, v in configs_dict.items() if isinstance(v, dict) and v.get('dns')}
        except (HTTPError, URLError):
            sys.exit('\nPIA VPN configurations were not able to be downloaded.' +
                     'This script needs an internet connection to be able to ' +
                     'fetch them automatically. Exiting.\n')

    def delete_old_configs(self):
        """
        Delete old Private Internet Access VPN configuration files. This will only
        delete files that are prefixed with 'PIA - '.

        """
        for f in os.listdir(self.config_dir):
            if f.startswith('PIA - '):
                os.remove('{}{}'.format(self.config_dir, f))


class Keyfile():

    def __init__(self, vpn_dict, username, password, **kwargs):
        self.config_dir = '/etc/NetworkManager/system-connections/'
        self.configs = vpn_dict
        self.cipher = kwargs.get('cipher', 'AES-128-CBC')
        self.auth = kwargs.get('auth', 'SHA1')
        self.port = kwargs.get('port', '1198')
        self.config_file = '{}{}{}'.format(self.config_dir, 'PIA - ', self.configs[1]['name'])
        self.define_keyfile(username, password)
        self.create_keyfile()

    def define_keyfile(self, username, password):
        l = ['[connection]', 'id={}{}', 'uuid={}', 'type=vpn', 'autoconnect=false',
             '\n', '[vpn]', 'service-type=org.freedesktop.NetworkManager.openvpn',
             'username={}', 'comp-lzo=yes', 'remote={}', 'connection-type=password',
             'password-flags=0', 'ca=/etc/openvpn/ca.rsa.2048.crt', 'port={}',
             'auth={}', 'cipher={}', '\n', '[vpn-secrets]',
             'password={}', '\n', '[ipv4]', 'method=auto']
        self.keyfile_string = '\n'.join(l).format('PIA - ', self.configs[1]['name'],
                                                  uuid.uuid4(), username,
                                                  self.configs[1]['dns'], self.port,
                                                  self.auth, self.cipher,
                                                  password)

    def create_keyfile(self):
        with open(self.config_file, 'w') as f:
            f.write(self.keyfile_string)
        os.chmod(self.config_file, 0o600)

    def __str__(self):
        return self.keyfile_string


class Connection():

    def __init__(self, region):
        self.region = region

    def get_pia_connections(self):
        if self.region == 'us':
            search_term = 'PIA - US'
        else:
            search_term = 'PIA - '
        sys_cons = '/etc/NetworkManager/system-connections/'
        if self.region == 'int':
            self.cons = [i for i in os.listdir(sys_cons) if (search_term in i) & ('US' not in i)]
        else:
            self.cons = [i for i in os.listdir(sys_cons) if search_term in i]

    def pick_rand_con(self):
        return self.cons[randint(0, len(self.cons) - 1)]

    def make_connection(self, con):
        print('Activating {}...'.format(con))
        subprocess.call(['nmcli', 'con', 'up', 'id', con])

    def connect_random_vpn(self):
        self.get_pia_connections()
        self.random_con = self.pick_rand_con()
        while self.random_con in self.active_pia:
            self.random_con = pick_rand_con(cons)
        self.make_connection(self.random_con)

    def disconnect_vpn(self):
        active_cons = subprocess.check_output(['nmcli', 'con', 'show', '--active']).decode('utf-8')
        self.active_pia = []
        for i in active_cons.split('\n'):
            if re.search('\svpn\s', i):
                vpn = re.split('\s+\S{36}\s+', i)[0]
                if vpn.startswith('PIA'):
                    self.active_pia.append(vpn)
        for i in self.active_pia:
            print('Disconnecting {}...'.format(i))
            subprocess.call(['nmcli', 'con', 'down', 'id', i])


class Latencies():

    def __init__(self, region):
        pia = PiaConfigurations()
        self.configs = pia.configs_dict
        self.q = Queue()
        self.latencies = {}
        self.get_ip_addresses(region)
        print('Pinging all PIA servers. This might take a few seconds...\n')
        self.threaded_pings()
        self.get_fastest()

    def get_ip_addresses(self, region):
        conn = Connection(region)
        conn.get_pia_connections()
        cons = [i.split(' - ')[-1] for i in conn.cons]
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

def main():
        parser = argparse.ArgumentParser(description='Connection tools for PIA VPNs.')
        parser.add_argument('-i', '--initialize', action='store_true',
                            help='configure pia vpn routes as networkmanager keyfiles. requires sudo priveleges. use this flag on first run and anytime you want to refresh pia vpn routes')
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

        def print_help_and_exit():
            parser.print_help()
            parser.exit(1)

        if not any(vars(args).values()):
            print_help_and_exit()

        if args.initialize:
            verify_running_as_root()
            distro = Distro()
            distro.install_packages()
            pia = PiaConfigurations()
            pia.get_credentials()
            pia.copy_cert()
            pia.delete_old_configs()
            for vpn_dict in pia.configs_dict.items():
                Keyfile(vpn_dict, pia.username, pia.password)
            distro.restart_network_manager()
            print("Creation of VPN config files was successful.\n")

        if not args.region:
            region = 'us'
        else:
            region = args.region
            if not any([args.ping, args.shuffle, args.fastest]):
                print_help_and_exit()
        conn = Connection(region)
        if args.disconnect:
            conn.disconnect_vpn()
        if args.fastest:
            conn.disconnect_vpn()
            lat = Latencies(region)
            print(lat)
            conn.make_connection(lat.fastest)
        elif args.ping:
            lat = Latencies(region)
            print(lat)
        if args.shuffle:
            conn.disconnect_vpn()
            conn.connect_random_vpn()

if __name__ == "__main__":
    main()
