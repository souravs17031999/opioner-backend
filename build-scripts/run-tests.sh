#!/usr/bin/env sh

source $WORKSPACE/build-scripts/env.sh

echo "Building Docker containers for apitest ..... "
docker-compose $apitest build
docker-compose $apitest down

echo "Starting all containers for test"
docker-compose $TEST_COMPOSE_LIST up --no-build --abort-on-container-exit
docker-compose $TEST_COMPOSE_LIST down -v