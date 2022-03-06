#!/usr/bin/env sh
set -ex 

export FLASK_APP=app.py
export FLASK_ENV=development 
export PYTHONUNBUFFERED="true"

source /app/env.sh

source /app/wait-for-db-server.sh 

if [[ "$REQUIRE_DB_MIGRATIONS" == "True" ]]; then 
    python3 migrations.py
fi

python3 -m flask run --host=0.0.0.0 --port=$PORT