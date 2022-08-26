#!/usr/bin/env bash
set -e 

if [[ -z $WORKSPACE ]]; then 
    TOPDIR=$(git rev-parse --show-toplevel)
    source $TOPDIR/opioner-commons/env.sh
else
    source $WORKSPACE/opioner-commons/env.sh
fi

echo "Building Docker containers for apitest ..... "
docker-compose $TEST_COMPOSE_LIST build $TEST_CONTAINER
docker-compose $TEST_COMPOSE_LIST down -v || true

echo "Starting all containers for test"
docker-compose $TEST_COMPOSE_LIST up --abort-on-container-exit --no-build
docker-compose $TEST_COMPOSE_LIST down -v