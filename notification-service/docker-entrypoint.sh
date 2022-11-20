#!/usr/bin/env bash
export FLASK_APP=app.py
export FLASK_ENV=development
export PYTHONUNBUFFERED="true"
source env.sh
source wait-for-db-server.sh

if [ -z "$PORT" ]
then
    echo "[Warning]: No PORT env found, setting it to default 8084 !"
    PORT=8084
fi

python3 -m flask run --host=0.0.0.0 --port=$PORT