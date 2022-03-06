#!/usr/bin/env sh

source $WORKSPACE/build-scripts/env.sh

echo "----- SENDING NOTIFICATION TO SLACK "

python build-scripts/publish.py