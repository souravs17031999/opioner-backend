#!/usr/bin/env bash

source $WORKSPACE/build-scripts/env.sh

echo "----- SENDING NOTIFICATION TO SLACK "

python3 build-scripts/publish.py