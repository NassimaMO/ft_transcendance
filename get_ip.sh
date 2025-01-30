#!/bin/bash

INTERFACE="Wi-Fi"

ipconfig.exe | awk -v iface="$INTERFACE" '
/^[A-Za-z]+/ { in_block = ($0 ~ iface) }
/IPv4/ && in_block { print $NF }
'