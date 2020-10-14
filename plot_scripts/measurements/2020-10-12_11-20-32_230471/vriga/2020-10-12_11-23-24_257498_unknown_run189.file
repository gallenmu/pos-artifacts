#!/bin/bash

# Script is run locally on experiment server.

# exit on error
set -e
# log every command
set -x

MOONGEN_DIR=$(pos_get_variable moongen_dir --from-global)
PKT_RATE=$(pos_get_variable pkt_rate --from-loop)
PKT_SZ=$(pos_get_variable pkt_sz --from-loop)

LOADGEN_INGRESS_DEV=$(pos_get_variable --from-global loadgen_ingress_dev)
LOADGEN_EGRESS_DEV=$(pos_get_variable --from-global loadgen_egress_dev)
LOADGEN_INGRESS_IF=$(pos_get_variable --from-global loadgen_ingress_if)
LOADGEN_EGRESS_IF=$(pos_get_variable --from-global loadgen_egress_if)
LOADGEN_INGRESS_MAC=$(pos_get_variable --from-global loadgen_ingress_mac)
LOADGEN_EGRESS_MAC=$(pos_get_variable --from-global loadgen_egress_mac)
LOADGEN_INGRESS_IP=$(pos_get_variable --from-global loadgen_ingress_ip)
LOADGEN_EGRESS_IP=$(pos_get_variable --from-global loadgen_egress_ip)
LOADGEN_ENABLE_IP_SW_CHKSUM_CALC=$(pos_get_variable --from-global loadgen_enable_ip_sw_chksum_calc)

LOADGEN_WARM_UP=$(pos_get_variable warm_up)

DUT_INGRESS_MAC=$(pos_get_variable --from-global dut_ingress_mac)
DUT_EGRESS_MAC=$(pos_get_variable --from-global dut_egress_mac)
DUT_INGRESS_IP=$(pos_get_variable --from-global dut_ingress_ip)
DUT_EGRESS_IP=$(pos_get_variable --from-global dut_egress_ip)

PKTS_TOTAL=$(($PKT_RATE*30))

echo "send packets with size: $PKT_SZ and rate: $PKT_RATE."

pos_sync

pos_run --loop loadgen -- bash -c "$MOONGEN_DIR/build/MoonGen $MOONGEN_DIR/examples/soft-gen.lua --src-mac $LOADGEN_EGRESS_MAC --dst-mac $DUT_INGRESS_MAC --src-ip $LOADGEN_EGRESS_IP --dst-ip $LOADGEN_INGRESS_IP --fix-packetrate $PKT_RATE --size $PKT_SZ --packets $PKTS_TOTAL --ip-chksum $LOADGEN_ENABLE_IP_SW_CHKSUM_CALC --warm-up $LOADGEN_WARM_UP $LOADGEN_EGRESS_DEV $LOADGEN_INGRESS_DEV > /root/throughput.log"

sleep 50

pos_kill --loop loadgen

sleep 100

pos_upload --loop /root/throughput.log

sleep 5

pos_sync

echo "experiment successful"
