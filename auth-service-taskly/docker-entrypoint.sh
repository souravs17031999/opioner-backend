#!/bin/sh

export FLASK_APP=app.py
export FLASK_ENV=development 
export PYTHONUNBUFFERED="true"

source env.sh

python3 migrations.py

python3 -m flask run --host=0.0.0.0 --port=8081