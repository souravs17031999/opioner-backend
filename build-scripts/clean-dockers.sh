#!/usr/bin/env bash

source $WORKSPACE/build-scripts/env.sh
echo "Cleaning up dockers"

docker-compose $BUILD_COMPOSE_LIST down --volumes --rmi local --remove-orphans
docker-compose down --rmi all || true 

echo "---------------------------------------------"