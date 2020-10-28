#!/bin/bash

# Setup of a simple experiment with two hosts involved.
#
# The hosts are allocated, rebooted, and the experiment scripts are deployed to the experiment
# hosts. The two experiment scripts just show how to deploy various variables to node scripts.
# Both experiment scripts create log files which are available on the current host after
# experiment execution.
#
# This script uses the loop mode of pos.
# There the experiment scripts are executed once for every possible combination of variables
# declared in the loop-variables.yml file.

if test "$#" -ne 2; then
	echo "Usage: setup.sh loadgen-experiment-node dut-experiment-node"
	exit
fi

echo "free hosts"
pos allocations free "$1"
pos allocations free "$2"

echo "allocate hosts"
pos allocations allocate "$1" "$2"

echo "set images to debian buster"
pos nodes image "$1" debian-buster
pos nodes image "$2" debian-buster

echo "load variables files"
pos allocations variables "$1" loadgen/variables.yml
pos allocations variables "$2" dut/variables.yml
# default (for all hosts) variables file
pos allocations variables "$1" global-variables.yml --as-global
# loop variables for experiment script
pos allocations variables "$1" loop-variables.yml --as-loop

echo "reboot experiment hosts..."
# run reset blocking in background and wait for processes to end before continuing
{ pos nodes reset "$1"; echo "$1 booted successfully"; } &
{ pos nodes reset "$2"; echo "$2 booted successfully"; } &
wait

echo "setup experiment hosts..."
{ pos commands launch --quiet --infile loadgen/setup.sh --blocking "$1"; } &
{ pos commands launch --quiet --infile dut/setup.sh --blocking "$2"; } &
wait

echo "execute experiment on hosts..."
{ pos commands launch --quiet --infile loadgen/measurement.sh --blocking --loop "$1"; } &
{ pos commands launch --quiet --infile dut/measurement.sh --blocking --loop "$2"; } &
wait

echo "free hosts"
pos allocations free "$1"
