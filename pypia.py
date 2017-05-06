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
if sys.version_info < (3,0):
    print("Sorry, this script requires python 3.x")
    sys.exit(1)
import os
import subprocess
import getpass
import uuid
import json
import urllib.request


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


def get_distro():
    """
    Get the name of the Linux distribution this script is being run on.

    Returns
    -------
    distro : str
        Short name for operating system listed in `/etc/os-release`
    """
    os_release = subprocess.check_output(['cat', '/etc/os-release']) \
        .decode('utf-8').splitlines()
    os_dict = {i.split('=')[0]: i.split('=')[1].strip('"')
               for i in os_release if '=' in i}
    distro = os_dict['ID'].lower()
    return distro


def install_packages(package_dict):
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
    distro = get_distro()
    required_packages = package_dict['required_packages'][distro]
    install_command = package_dict['install_commands'][distro]
    for package in required_packages:
        raw = input('Installing {}. OK? (y/n): '.format(package))
        if (raw.lower() == 'y') | (raw.lower() == 'yes'):
            os.system(install_command.format(package))
        else:
            sys.exit('\n{} required. Exiting.\n'.format(package))


def get_credentials():
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
    username = input('\nEnter your PIA username: ')
    while True:
        password = getpass.getpass(prompt='Enter your password: ')
        password2 = getpass.getpass(prompt='Please re-enter password: ')
        if password == password2: break
        print("\nPasswords do not match. Please re-enter:")
    return username, password


def copy_cert():
    """
    Download and save Private Internet Access certificate to
    `/etc/openvpn/ca.rsa.2048.crt`.

    An internet connection is needed if cert hasn't already been downloaded.
    If for some reason the cert is not able to be downloaded, or if it hasn't
    previously been downloaded and saved to `/etc/openvpn/ca.rsa.2048.crt`, the script
    will exit.

    """
    cert_address = 'https://www.privateinternetaccess.com/openvpn/ca.rsa.2048.crt'
    try:
        urllib.request.urlretrieve(cert_address, '/etc/openvpn/ca.rsa.2048.crt')
        if os.path.exists('/etc/openvpn/ca.rsa.2048.crt'):
            print('PIA certificate downloaded and saved to /etc/openvpn/')
    except (HTTPError, URLError):
        sys.exit('\nPIA cert was not able to be downloaded and saved. ' +
                 'This script needs an internet connection to be able to' +
                 'fetch it automatically. Exiting.\n')


def get_vpn_configs():
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
    config_address = 'https://privateinternetaccess.com/vpninfo/servers'
    try:
        with urllib.request.urlopen(config_address) as url:
            config_json = url.read().decode('utf-8').split('\n')[0]
        configs_dict = json.loads(config_json)
        return configs_dict
    except (HTTPError, URLError):
        sys.exit('\nPIA VPN configurations were not able to be downloaded.' +
                 'This script needs an internet connection to be able to ' +
                 'fetch them automatically. Exiting.\n')


def delete_old_configs():
    """
    Delete old Private Internet Access VPN configuration files. This will only
    delete files that are prefixed with 'PIA - '.

    """
    config_dir = '/etc/NetworkManager/system-connections/'
    for f in os.listdir(config_dir):
        if f.startswith('PIA - '):
            os.remove('{}{}'.format(config_dir, f))


def output_config_file(vpn_dict):
    """
    Create a Network Manager openvpn configuration file from a configuration
    dictionary, such as those found in `configs_dict`.

    Designed to be used in a loop to loop over all dictionaries in
    `configs_dict`

    Permissions of created file is changed to `rw` for root only to protect
    username and password from non-root users.

    Parameters
    ----------
    vpn_dict : dict
        Dictionary with PIA VPN server configuration information.

    """
    config_dir = '/etc/NetworkManager/system-connections/'
    config_file = '{}{}{}'.format(config_dir, 'PIA - ', vpn_dict['name'])
    with open(config_file, 'w') as f:
        f.write('[connection]\n')
        f.write('id={}{}\n'.format('PIA - ', vpn_dict['name']))
        f.write('uuid={}\n'.format(uuid.uuid4()))
        f.write('type=vpn\n')
        f.write('autoconnect=false\n\n')
        f.write('[vpn]\n')
        f.write('service-type=org.freedesktop.NetworkManager.openvpn\n')
        f.write('username={}\n'.format(username))
        f.write('comp-lzo=yes\n')
        f.write('remote={}\n'.format(vpn_dict['dns']))
        f.write('connection-type=password\n')
        f.write('password-flags=0\n')
        f.write('ca=/etc/openvpn/ca.rsa.2048.crt\n')
        f.write('port=1198\n')
        f.write('auth=SHA1\n')
        f.write('cipher=AES-128-CBC\n\n')
        f.write('[vpn-secrets]\n')
        f.write('password={}\n\n'.format(password))
        f.write('[ipv4]\n')
        f.write('method=auto\n')
    os.chmod(config_file, 0o600)


def restart_network_manager():
    """
    Use `systemctl` (systemd) command to restart the Network Manager service.

    Notes
    -----
        This will not work on systems without systemd.

    """
    print('Restarting network manager...')
    os.system('systemctl restart NetworkManager.service')


if __name__ == "__main__":
    verify_running_as_root()
    with open('./package_info.json', 'r') as package_info:
        package_dict = json.load(package_info)
    install_packages(package_dict)
    username, password = get_credentials()
    copy_cert()
    configs_dict = get_vpn_configs()
    delete_old_configs()
    for vpn_dict in configs_dict:
        try:
            output_config_file(configs_dict[vpn_dict])
        except (KeyError, TypeError):
            pass
    restart_network_manager()
    print("Creation of VPN config files was successful.\n")
