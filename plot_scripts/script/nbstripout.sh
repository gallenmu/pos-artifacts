#! /bin/bash

if [ $# -eq 1 ]; then
	set -x
	nbstripout $1
else
	set -x
	nbstripout *.ipynb util/*.ipynb
fi
