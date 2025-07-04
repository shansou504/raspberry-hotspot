#!/bin/bash

###############################################################################
# This script creates a wifi hotspot bridged to ethernet on a Raspberry Pi
# running the latest RaspiOS Lite. If an additional outgoing ethernet
# connection is used via USB adapter it will also be added to the bridge.
#
# To access the directories this script must be run as root.
#
# It is assumed that wifi has already been enabled by running
# raspi-config and selecting a country code.
###############################################################################

# Update system and install dependencies
apt update
apt full-upgrade -y
apt install -y netplan.io

# Prompt for SSID and psk
echo -ne "\nEnter an SSID for the new access point (must not include "
echo -ne "spaces): "
read ssid
echo -ne "Enter a password for the new access point (must be a minimum "
echo -ne "of 8 characters): "
read psk

# Write netplan yaml
echo -e "\nWriting to /etc/netplan/00-ap.yaml ..."
umask 177
cat <<EOF > /etc/netplan/00-ap.yaml && echo "...success" || echo "...failed to create 00-ap.yaml"
network:
  version: 2
  renderer: NetworkManager
  ethernets:
    eth0:
      dhcp4: false
      optional: true
    eth1:
      dhcp4: false
      optional: true
  wifis:
    wlan0:
      dhcp4: false
      optional: true
      access-points:
        "$ssid":
          mode: ap
          password: "$psk"
          networkmanager:
            passthrough:
              connection.master: br0
              connection.slave-type: bridge
              ipv4.method: disabled
              bridge-port.priority: 32
              bridge-port.path-cost: 100
              bridge-port.hairpin-mode: no
              802-11-wireless.powersave: 2
              802-11-wireless-security.pairwise: ccmp
              802-11-wireless-security.proto: rsn
  bridges:
    br0:
      dhcp4: true
      optional: true
      interfaces:
        - eth0
        - eth1
        - wlan0
EOF

# Display netplan yaml
echo ""
cat /etc/netplan/00-ap.yaml

# Prompt for reboot
echo -ne "\nReboot to make changes take effect? (Y/n): "
read reboot_yn

# Reboot
if [ $reboot_yn == "Y" ] || [ $reboot_yn == "y" ]; then
    systemctl reboot
else
    echo -e "\nThe system will not reboot."
fi
