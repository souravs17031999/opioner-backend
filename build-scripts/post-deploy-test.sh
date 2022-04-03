#!/usr/bin/env bash

if [[ -z $WORKSPACE ]]; then 
    TOPDIR=$(git rev-parse --show-toplevel)
    source $TOPDIR/build-scripts/env.sh
else
    source $WORKSPACE/build-scripts/env.sh
fi

echo "Building Docker containers for apitest ..... "
docker-compose $POST_DEPLOY_COMPOSE_TEST build
docker-compose $POST_DEPLOY_COMPOSE_TEST down -v || true

echo "Starting all containers for test"
docker-compose $POST_DEPLOY_COMPOSE_TEST up --abort-on-container-exit --no-build
docker-compose $POST_DEPLOY_COMPOSE_TEST down -v