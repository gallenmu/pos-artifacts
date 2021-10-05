#!/bin/bash

# Script is run locally on experiment server.

# exit on error
set -e
# log every command
#set -x

MOONGEN_REPO=$(pos_get_variable moongen_repo --from-global)
MOONGEN_REPO_COMMIT=$(pos_get_variable moongen_repo_commit --from-global)
MOONGEN_DIR=$(pos_get_variable moongen_dir --from-global)

LOADGEN_INGRESS_IF=$(pos_get_variable --from-global loadgen_ingress_if)
LOADGEN_EGRESS_IF=$(pos_get_variable --from-global loadgen_egress_if)
LOADGEN_INGRESS_MAC=$(pos_get_variable --from-global loadgen_ingress_mac)
LOADGEN_EGRESS_MAC=$(pos_get_variable --from-global loadgen_egress_mac)
LOADGEN_INGRESS_IP=$(pos_get_variable --from-global loadgen_ingress_ip)
LOADGEN_EGRESS_IP=$(pos_get_variable --from-global loadgen_egress_ip)

#ip link set dev $LOADGEN_INGRESS_IF up
#ip link set dev $LOADGEN_EGRESS_IF up
#ip link set dev $LOADGEN_INGRESS_IF address $LOADGEN_INGRESS_MAC
#ip link set dev $LOADGEN_EGRESS_IF address $LOADGEN_EGRESS_MAC
#ip addr add $LOADGEN_INGRESS_IP/24  dev $LOADGEN_INGRESS_IF
#ip addr add $LOADGEN_EGRESS_IP/24 dev $LOADGEN_EGRESS_IF

git clone "$MOONGEN_REPO" "$MOONGEN_DIR"
cd "$MOONGEN_DIR"
git checkout "$MOONGEN_REPO_COMMIT"
"$MOONGEN_DIR"/build.sh
"$MOONGEN_DIR"/bind-interfaces.sh
"$MOONGEN_DIR"/setup-hugetlbfs.sh

echo "setup successful"
