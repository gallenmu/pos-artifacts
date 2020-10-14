#!/bin/bash

# Script is run locally on experiment server.

# exit on error
set -e
# # log every command
set -x

PKT_RATE=$(pos_get_variable pkt_rate --from-loop)
PKT_SZ=$(pos_get_variable pkt_sz --from-loop)

echo "forward packets with size: $PKT_SZ and rate: $PKT_RATE."

pos_sync

sleep 1

pos_sync

echo "experiment successful"
