from setuptools import setup

setup(
    name = 'pypia',
    packages = ['pypia'],
    version = '0.1.2',
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

Configures NetworkManager keyfiles for OpenVPN routes to PIA servers. 

pypia has been designed to automatically detect your operating system.

Currently the supported distros are Fedora, Manjaro, Ubuntu, Elementary OS, Antergos, Linuxmint, openSUSE, Kali, Arch

This module is meant to be used as a command line tool.

In addition to configuring NetworkManager keyfiles, this module also can be invoked to ping all PIA endpoints, connect to the fastest, connect to a random server, etc. Use `pypia --help` for further descriptions and usage.

This module requires Python 3; Python 2 is not supported.
"""
)
