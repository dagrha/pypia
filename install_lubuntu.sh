#! /bin/sh -
#
# Install OpenVPN connections for all available
# regions to NetworkManager
#
# Requirements:
#   should be run as root
#   python, openvpn, uuidgen (will be installed if not present)
#
# Usage:
#  install [--version]

IFS='
	 '
SERVER_INFO=/tmp/server_info
SPLIT_TOKEN=':'

error( )
{
  echo "$@" 1>&2
  exit 1
}

error_and_usage( )
{
  echo "$@" 1>&2
  usage_and_exit 1
}

usage( )
{
  echo "Usage: sudo `dirname $0`/$PROGRAM"
}

usage_and_exit( )
{
  usage
  exit $1
}

version( )
{
  echo "$PROGRAM version $VERSION"
}

read_user_login( )
{
  echo -n "Please enter your login: "
  read LOGIN
  if [ -z $LOGIN ]; then
    error "A login must be provided for the installation to proceed"
  fi
}

verify_running_as_root( )
{
  if [ `/usr/bin/id -u` -ne 0 ]; then
      error_and_usage "$0 must be run as root"
  fi
}

install_python( )
{
  if ! dpkg -l python | grep '^ii' > /dev/null ; then
    echo -n 'Package python required. Install? (y/n): '
    read install_python
    if [ $install_python = 'y' ]; then
      echo "Installing python.."
      if ! apt install python; then
        error "Error installing python. Aborting.."
      fi
    else
      error "Package python is required for installation. Aborting.."
    fi
  else
    echo "Package python already installed"
  fi
}

install_open_vpn( )
{
  if ! dpkg -l network-manager-openvpn | grep '^ii' > /dev/null ; then
    echo -n 'Package network-manager-openvpn required. Install? (y/n): '
    read install_openvpn
    if [ $install_openvpn = 'y' ]; then
      echo "Installing network-manager-openvpn.."
      if ! apt install network-manager-openvpn; then
        error "Error installing network-manager-openvpn. Aborting.."
      fi
    else
      error "Package network-manager-openvpn is required for installation. Aborting.."
    fi
  else
    echo "Package network-manager-openvpn already installed"
  fi
}

install_uuidgen( )
{
  if ! dpkg -l uuid-runtime | grep '^ii' > /dev/null ; then
    echo -n 'Package uuid-runtime required. Install? (y/n): '
    read install_uuidruntime
    if [ $install_uuidruntime = 'y' ]; then
      echo "Installing uuid-runtime.."
      if ! apt-get install uuid-runtime; then
        error "Error installing uuid-runtime. Aborting.."
      fi
    else
      error "Package uuid-runtime is required for installation. Aborting.."
    fi
  else
    echo "Package uuid-runtime already installed"
  fi
}

copy_crt( )
{
  echo 'Copying certificate..'
  mkdir -p /etc/openvpn
cat << EOF > /etc/openvpn/ca.crt
-----BEGIN CERTIFICATE-----
MIID2jCCA0OgAwIBAgIJAOtqMkR2JSXrMA0GCSqGSIb3DQEBBQUAMIGlMQswCQYD
VQQGEwJVUzELMAkGA1UECBMCT0gxETAPBgNVBAcTCENvbHVtYnVzMSAwHgYDVQQK
ExdQcml2YXRlIEludGVybmV0IEFjY2VzczEjMCEGA1UEAxMaUHJpdmF0ZSBJbnRl
cm5ldCBBY2Nlc3MgQ0ExLzAtBgkqhkiG9w0BCQEWIHNlY3VyZUBwcml2YXRlaW50
ZXJuZXRhY2Nlc3MuY29tMB4XDTEwMDgyMTE4MjU1NFoXDTIwMDgxODE4MjU1NFow
gaUxCzAJBgNVBAYTAlVTMQswCQYDVQQIEwJPSDERMA8GA1UEBxMIQ29sdW1idXMx
IDAeBgNVBAoTF1ByaXZhdGUgSW50ZXJuZXQgQWNjZXNzMSMwIQYDVQQDExpQcml2
YXRlIEludGVybmV0IEFjY2VzcyBDQTEvMC0GCSqGSIb3DQEJARYgc2VjdXJlQHBy
aXZhdGVpbnRlcm5ldGFjY2Vzcy5jb20wgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJ
AoGBAOlVlkHcxfN5HAswpryG7AN9CvcvVzcXvSEo91qAl/IE8H0knKZkIAhe/z3m
hz0t91dBHh5yfqwrXlGiyilplVB9tfZohvcikGF3G6FFC9j40GKP0/d22JfR2vJt
4/5JKRBlQc9wllswHZGmPVidQbU0YgoZl00bAySvkX/u1005AgMBAAGjggEOMIIB
CjAdBgNVHQ4EFgQUl8qwY2t+GN0pa/wfq+YODsxgVQkwgdoGA1UdIwSB0jCBz4AU
l8qwY2t+GN0pa/wfq+YODsxgVQmhgaukgagwgaUxCzAJBgNVBAYTAlVTMQswCQYD
VQQIEwJPSDERMA8GA1UEBxMIQ29sdW1idXMxIDAeBgNVBAoTF1ByaXZhdGUgSW50
ZXJuZXQgQWNjZXNzMSMwIQYDVQQDExpQcml2YXRlIEludGVybmV0IEFjY2VzcyBD
QTEvMC0GCSqGSIb3DQEJARYgc2VjdXJlQHByaXZhdGVpbnRlcm5ldGFjY2Vzcy5j
b22CCQDrajJEdiUl6zAMBgNVHRMEBTADAQH/MA0GCSqGSIb3DQEBBQUAA4GBAByH
atXgZzjFO6qctQWwV31P4qLelZzYndoZ7olY8ANPxl7jlP3YmbE1RzSnWtID9Gge
fsKHi1jAS9tNP2E+DCZiWcM/5Y7/XKS/6KvrPQT90nM5klK9LfNvS+kFabMmMBe2
llQlzAzFiIfabACTQn84QLeLOActKhK8hFJy2Gy6
-----END CERTIFICATE-----
EOF

}

parse_server_info( )
{
  echo 'Loading servers information..'
  json=`wget -q -O - 'https://raw.githubusercontent.com/dagrha/PIA_install_scripts/master/routes.json' | head -1`

  python > $SERVER_INFO <<EOF
payload = '$json'
import json
d = json.loads(payload)
print("\n".join([d[k]['name']+'$SPLIT_TOKEN'+d[k]['dns'] for k in d.keys() if k != 'info']))
EOF
}

write_config_files( )
{
  echo 'Removing previous config files if existing..'
  rm -f /etc/NetworkManager/system-connections/PIA\ -\ *

  echo 'Creating config files..'
  IFS='
'
  while read server_info; do
    name="PIA - `echo $server_info | awk -F: '{print $1}'`"
    dns=`echo $server_info | awk -F: '{print $2}'`
    cat <<EOF > /etc/NetworkManager/system-connections/$name
[connection]
id=$name
uuid=`uuidgen`
type=vpn
autoconnect=false

[vpn]
service-type=org.freedesktop.NetworkManager.openvpn
username=$LOGIN
comp-lzo=yes
remote=$dns
connection-type=password
password-flags=1
ca=/etc/openvpn/ca.crt

[ipv4]
method=auto
EOF
  chmod 600 /etc/NetworkManager/system-connections/$name
  done < $SERVER_INFO
  rm $SERVER_INFO
  IFS='
 	'
}

restart_network_manager( )
{
  echo 'Restarting network manager..'
  service network-manager restart 
}

EXITCODE=0
PROGRAM=`basename $0`
VERSION=1.0

while test $# -gt 0
do
  case $1 in
  --usage | --help | -h )
    usage_and_exit 0
    ;;
  --version | -v )
    version
    exit 0
    ;;
  *)
    error_and_usage "Unrecognized option: $1"
    ;;
  esac
  shift
done


verify_running_as_root
install_python
install_open_vpn
install_uuidgen
read_user_login
copy_crt
parse_server_info
write_config_files
restart_network_manager

echo "Install successful!"
exit 0
