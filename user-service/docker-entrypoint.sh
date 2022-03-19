#!/usr/bin/env bash
export FLASK_APP=app.py
export FLASK_ENV=development
export PYTHONUNBUFFERED="true"
source env.sh
source wait-for-db-server.sh
if [[ "$APM_MONITORING_NEWRELIC" == "True" ]]; then
    echo "Starting with APM monitoring (NewRelic)"
    NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program python3 -m flask run --host=0.0.0.0 --port=$PORT
else
    python3 -m flask run --host=0.0.0.0 --port=$PORT
fi