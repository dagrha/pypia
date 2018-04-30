from setuptools import setup

setup(
    name = 'pypia',
    packages = ['pypia'],
    version = '0.3.4',
    package_data = {'pypia': ['package_info.json']},
    author = 'Dan Hallau',
    author_email = 'pia@hallau.us',
    url = 'https://github.com/dagrha/pypia',
    description = 'Configuration and connection tools for PIA VPN routes on Linux',
    keywords = [],
    entry_points = {
        'console_scripts': ['pypia=pypia.pypia:main',],
    },
    classifiers = [
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Internet",
        "Topic :: Internet :: Proxy Servers"
    ],
    long_description = """\
Private Internet Access configuration package for various Linux distributions
-----------------------------------------------------------------------------

Configures NetworkManager keyfiles for OpenVPN routes to Private Internet Access servers.

pypia automatically detects your operating system. Currently the supported distros are Fedora, Manjaro, Ubuntu, Elementary OS, Antergos, Linuxmint, openSUSE, Kali, Arch, CentOS.

In addition to configuring NetworkManager keyfiles, this module also can be invoked to ping all PIA endpoints, connect to the fastest, connect to a random server, etc. Use `pypia --help` for further descriptions and usage.

    usage: pypia.py [-h] [-i] [-p] [-s] [-r {us,all,int}] [-f] [-d]

    optional arguments:
      -h, --help            show this help message and exit
      -i, --initialize      configure pia vpn routes as networkmanager keyfiles. use this flag on first run and anytime you want to refresh pia vpn routes
      -p, --ping            ping each vpn server and list latencies
      -s, --shuffle         connect to or shuffle a random vpn
      -r, --region          "us" for US only, "int" for non-US, "all" for worldwide
      -f, --fastest         connect to network with lowest ping latency
      -d, --disconnect      disconnect current PIA vpn connection

"""
)
