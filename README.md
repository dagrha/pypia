## Private Internet Access installation scripts for various Linux distributions

While [Private Internet Access](https://www.privateinternetaccess.com/) (PIA) provides high quality and inexpensive VPN services, the process of setting up easy-to-use VPN routes that are accessible from the NetworkManager applet GUI on Linux is not as straight-forward as it should be. The purpose of this repository is to host and maintain installation scripts that will automatically populate NetworkManager VPN routes for use with PIA OpenVPN service on various Linux distributions.

The scripts found in this repository are based on an installation script provided by PIA [here](https://www.privateinternetaccess.com/pages/client-support/ubuntu-openvpn). Unfortunately those instructions for installation apply only to Ubuntu 12.04, and in their current form are not extensible to other Linux distributions, even some of those that are in the Ubuntu family (e.g. Lubuntu).

#### Currently supported distributions
* Fedora 23
* OpenSUSE Tumbleweed, Leap
* Manjaro 15
* Ubuntu flavors:
 * Ubuntu 16.04
 * Lubuntu 16.04

#### Requirements
* System
 * network manager
 * python
 * network-manager-openvpn
 * uuidgen (part of the uuid-runtime toolset)
The script checks for the *python*, *network-manager-openvpn*, and *uuidgen* dependencies and will install them if they are missing. It is assumed that NetworkManager will already be installed, since it comes by default on many distibutions, but that may not be the case for Arch, etc.

* General
 * PIA subscription (which is a pay service).

#### Other information
PIA certificate information is hosted in the install scripts themselves. The certificate is an exact replica of that provided by PIA [here](https://www.privateinternetaccess.com/installer/install_ubuntu.sh).
Route/VPN server information is downloaded from [this page](https://www.privateinternetaccess.com/vpninfo/servers?version=24). As you can see, a route information `version` can be specified. Here we've specified version 24 to be the default, since that is what is specified in the original PIA script, but that can be changed as needed, if you can figure out why you'd want one version over another. The routes v24 json is also hosted in this repository for convenience and reference but is not used in the acutal installation.

#### Installation
1. Either download one of the installation scripts from this repo directly, or clone the github repository to your local workstation.
2. `cd` to the directory where the script(s) were downloaded.   

   e.g. `cd ~/git/PIA_install_scripts` or `cd ~/Downloads`
   
3. Run the following command in the terminal:

   `sudo sh ./install_fedora.sh`
   Change `install_fedora.sh` to the name of the `.sh` script that matches the distribution you are using (e.g. `install_ubuntu.sh`, etc.) 
   
4. Since the script needs root permissions to install dependencies, you will be prompted to enter your sudoer's password. 
5. At some point in the installation process you will be prompted for your PIA-issued user ID (typically starts with a `p` and is followed by a bunch of numbers).
6. If everything goes as intended, the VPN routes will be accessible from the *VPN Connections* menu in the NetworkManager applet.

#### Contributions
While not required, any improvements for existing scripts or modifications that add applicability to other distros is greatly appreciated and encouraged.
