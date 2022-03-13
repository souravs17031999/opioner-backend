#!/usr/bin/env bash

if [ "$TEST_SUITE_DIR" = "apitest" ]; then
    source wait-for-db-server.sh
fi

source run-tests.sh
