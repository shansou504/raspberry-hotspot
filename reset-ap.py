#!/usr/bin/env python3

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

import os
import subprocess

# Update system and install dependencies
subprocess.run(["apt","update"])
subprocess.run(["apt","full-upgrade","-y"])
subprocess.run(["apt","install","-y","netplan.io"])

# Prompt for SSID and psk
print("\nEnter an SSID for the new access point (must not include ", end="")
ssid = input("spaces): ")
print("Enter a password for the new access point (must be a minimum ", end="")
psk = input("of 8 characters): ")

# Write netplan yaml
netplan_file = "/etc/netplan/00-ap.yaml"
print(f"\nWriting to {netplan_file} ...")
try:
    os.remove(netplan_file)
except FileNotFoundError:
    pass
with open(netplan_file,"x") as netplan:
    netplan.write(
f"""network: 
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
        "{ssid}":
          mode: ap
          password: "{psk}"
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
""")

# Display netplan yaml
with open(netplan_file, "r") as netplan:
    print(netplan.read())

# Change permissions on netplan yaml
os.chmod(netplan_file, 0o100)

# Prompt for reboot
reboot_yn = input("\nReboot to make changes take effect? (Y/n): ")

# Reboot
if reboot_yn in ["Y","y" ]:
    subprocess.run(["systemctl","reboot"])
else:
    print("\nThe system will not reboot.")
