#!/usr/bin/env bash
set -e 

if [[ -z $WORKSPACE ]]; then 
    TOPDIR=$(git rev-parse --show-toplevel)
    source $TOPDIR/opioner-commons/env.sh
else
    source $WORKSPACE/opioner-commons/env.sh
fi

echo "----- SENDING NOTIFICATION TO SLACK "

python3 opioner-commons/publish.py