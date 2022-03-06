#!/usr/bin/env sh

source $WORKSPACE/build-scripts/env.sh

echo "----------------- Building Docker containers for apitest ..... "

docker-compose $TEST_COMPOSE_LIST up --no-build --abort-on-container-exit
docker-compose $TEST_COMPOSE_LIST down -v