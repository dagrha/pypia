## Private Internet Access configuration scripts for various Linux distributions

[Private Internet Access](https://www.privateinternetaccess.com/) (PIA) provides high quality and inexpensive VPN services, but installing VPN routes on linux can be tedious or require the installation of third party software. The purpose of this repository is to host and maintain installation scripts that will automatically populate NetworkManager VPN routes for use with PIA OpenVPN service on various Linux distributions and to avoid the installation of any third party programs.

This project was originally a set of shell scripts under the name `PIA_install_scripts`, but the project now consists of a single python script, which I'm calling **pypia.py**. The shell scripts are still accessible in the /legacy_scripts/ directory but are no longer supported.

#### Currently supported distributions
The script has been designed to automatically detect your operating system. Currently the supported distros are:
* Fedora
* Manjaro
* Ubuntu (various flavors, e.g. Lubuntu, should also work)
* Elementary OS
* Antergos
* Linuxmint

***For other distros, please see note at end of this README***

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
1. Either download `pypia.py` and `package_info.json` from this repo directly, or clone the github repository to your local workstation.
2. `cd` to the directory where the script was downloaded.   

   e.g. `cd ~/git/pypia/` or `cd ~/Downloads/`

3. Run the following command in the terminal:

   `sudo python3 pypia.py`

   In some distributions, `python` PATH variable points to Python 3, but in others it points to Python 2. Specifying `python3` will usually work.

4. Since the script needs root permissions to install dependencies via the package manager and to write the VPN config files to `/etc/NetworkManager/system-connections/`, you will be prompted to enter the root password.
5. At some point in the installation process you will be prompted for your PIA-issued user ID (typically starts with a "p" and is followed by a bunch of numbers). You will also be prompted for your password, which is simply saved to the config files (in plain text, but only root user can view/edit those files).
6. If everything goes as intended, the VPN routes will be accessible from the *VPN Connections* menu in the NetworkManager applet.

#### Contributions
If your distribution of choice is not currently listed as supported, please take a minute to help me add support! To add it, I'll need to know:
1. The specific name of the `network-manager-openvpn` package in your particular package manager. Usually searching the package database for "openvpn" is enough to find it.
1. The install command for your package manager (e.g. `apt install` or `dnf install`, etc.)
1. At a python (3+) prompt, enter the following commands and let me know what the string returned from the `get_distro()` function is:
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
