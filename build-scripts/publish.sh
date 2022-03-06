#!/usr/bin/env sh

source $WORKSPACE/build-scripts/env.sh

echo "----- SENDING NOTIFICATION TO SLACK "

PY build-scripts/publish.py