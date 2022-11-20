#!/usr/bin/env bash
export FLASK_APP=app.py
export FLASK_ENV=development
export PYTHONUNBUFFERED="true"
source env.sh
source wait-for-db-server.sh
if [[ "$REQUIRE_DB_MIGRATIONS" == "True" ]]; then
    python3 migrations.py
fi

if [ -z "$PORT" ]
then
    echo "[Warning]: No PORT env found, setting it to default 8081 !"
    PORT=8081
fi

python3 -m flask run --host=0.0.0.0 --port=$PORT
