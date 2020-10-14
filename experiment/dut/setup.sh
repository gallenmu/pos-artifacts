#!/bin/bash

# Script is run locally on experiment server.

# exit on error
set -e
# log every command
# set -x

# get variables
DUT_INGRESS_IF=$(pos_get_variable --from-global dut_ingress_if)
DUT_EGRESS_IF=$(pos_get_variable --from-global dut_egress_if)
DUT_INGRESS_MAC=$(pos_get_variable --from-global dut_ingress_mac)
DUT_EGRESS_MAC=$(pos_get_variable --from-global dut_egress_mac)
DUT_INGRESS_IP=$(pos_get_variable --from-global dut_ingress_ip)
DUT_EGRESS_IP=$(pos_get_variable --from-global dut_egress_ip)

LOADGEN_INGRESS_MAC=$(pos_get_variable --from-global loadgen_ingress_mac)
LOADGEN_INGRESS_IP=$(pos_get_variable --from-global loadgen_ingress_ip)

# config interfaces
ip link set dev $DUT_INGRESS_IF up
ip link set dev $DUT_EGRESS_IF up
ip link set dev $DUT_INGRESS_IF address $DUT_INGRESS_MAC
ip link set dev $DUT_EGRESS_IF address $DUT_EGRESS_MAC
ip addr add $DUT_INGRESS_IP/24 dev $DUT_INGRESS_IF
ip addr add $DUT_EGRESS_IP/24 dev $DUT_EGRESS_IF

# create static ARP entries (MoonGen script does not answer ARP requests)
ip neighbor add $LOADGEN_INGRESS_IP lladdr $LOADGEN_INGRESS_MAC dev $DUT_EGRESS_IF nud permanent

# enable linux router
sysctl -w net.ipv4.ip_forward=1

echo "setup successful"


