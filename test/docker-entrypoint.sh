#!/usr/bin/env bash

if [ "$TEST_SUITE_DIR" = "apitest" ]; then
    export AUTH_SERVER_URL="http://auth_service:8081/auth/status/live"
elif [ "$TEST_SUITE_DIR" = "postdeploy" ]; then
    export AUTH_SERVER_URL="http://auth-service-prd.herokuapp.com/auth/status/live"
fi

source wait-for-db-server.sh
source run-tests.sh
