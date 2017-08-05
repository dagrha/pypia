## Private Internet Access OpenVPN configuration package for various Linux distributions

[Private Internet Access](https://www.privateinternetaccess.com/pages/buy-vpn/pypia) (PIA) provides high quality and inexpensive VPN services, but installing VPN routes on linux can be tedious or require the installation of third party applets. The purpose of this repository is to host and maintain a configuration package that will automatically populate NetworkManager keyfiles for use with PIA OpenVPN service on various Linux distributions and to avoid the installation of any third party applets.

#### Quickstart
Install with `pip install pypia`

On first run, start with `pypia -i`.

#### Currently supported distributions
The `pypia` package has been designed to automatically detect your operating system. Currently the supported distros are:
* Fedora
* Manjaro
* Ubuntu (various flavors, e.g. Lubuntu, should also work)
* Elementary OS
* Antergos
* Linuxmint
* openSUSE
* Kali
* Arch

****For other distros, please see note at end of this README***

#### Requirements
* System
  * Python 3. This script is written in Python 3. Python 2 is not supported.
  * network manager
  * openvpn  
The script installs the *network-manager-openvpn* package (name of package may be different depending on your distribution).

* General
  * PIA subscription (which is a pay service).

#### Other information
PIA certificate, which is automatically downloaded by the script, is provided by PIA [here](https://www.privateinternetaccess.com/openvpn/ca.crt).
Route/VPN server information is downloaded from [this page](https://www.privateinternetaccess.com/vpninfo/servers).

#### Installation
1. You can use pip to install this module:
`pip install pypia`
2. Once installed via `pip`, you should do `pypia -i` to initialize, which will configure the NetworkManager keyfiles. Root permissions are required to install dependencies via the package manager and to write the VPN config files to `/etc/NetworkManager/system-connections/`, so you will be prompted to enter the root password.
3. At some point in the installation process you will be prompted for your PIA-issued user ID (typically starts with a "p" and is followed by a bunch of numbers). You will also be prompted for your password, which is simply saved to the config files (in plain text, but only root user can view/edit those files).

If everything goes as intended, the VPN routes will be accessible from the *VPN Connections* menu in the NetworkManager applet or via the `nmcli` command line tool.

##### Other features

    usage: pypia [-h] [-i] [-p] [-s] [-r {us,all,int}] [-f] [-d]

    optional arguments:
      -h, --help            show this help message and exit
      -i, --initialize      configure pia vpn routes as networkmanager keyfiles.
                            requires sudo priveleges. use this flag on first run
                            and anytime you want to refresh pia vpn routes
      -p, --ping            ping each vpn server and list latencies
      -s, --shuffle         connect to or shuffle a random vpn
      -r {us,all,int}, --region {us,all,int}
                            "us" for US only, "int" for non-US, "all" for
                            worldwide
      -f, --fastest         connect to network with lowest ping latency
      -d, --disconnect      disconnect current PIA vpn connection

### Contributions
If your distribution of choice is not currently listed as supported, please take a minute to help me add support! To add it, I'll need to know:

1. The specific name of the `network-manager-openvpn` package in your particular package manager. Usually searching the package database for "openvpn" is enough to find it.
2. The install command for your package manager (e.g. `apt install` or `dnf install`, etc.)
3. At a python (3+) prompt, enter the following commands and let me know what the string returned from the `get_distro()` function is:
```
import subprocess
def get_distro():
    os_release = subprocess.check_output(['cat', '/etc/os-release']).decode('utf-8').splitlines()
    os_dict = {i.split('=')[0]: i.split('=')[1].strip('"') for i in os_release if '=' in i}
    distro = os_dict['ID'].lower()
    return distro
get_distro()
```
With that information, I can update the `package_info.json` file to include your distro. Or feel free to submit a pull request.

#### License
The python code in this project is distributed under GPLv3.

If you want to [sign up for PIA](https://www.privateinternetaccess.com/pages/buy-vpn/pypia), feel free to use [my affiliate link](https://www.privateinternetaccess.com/pages/buy-vpn/pypia). If you'd rather not use that link, no worries! This is free software that I hope you continue to use and enjoy.
