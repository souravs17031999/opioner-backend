#!/usr/bin/env bash

if [[ -z $WORKSPACE ]]; then 
    TOPDIR=$(git rev-parse --show-toplevel)
    source $TOPDIR/build-scripts/env.sh
else
    source $WORKSPACE/build-scripts/env.sh
fi

echo "Cleaning up dockers"

docker-compose $BUILD_COMPOSE_LIST down --volumes --rmi local --remove-orphans
docker-compose down --rmi all || true 
echo "Pruning images"
docker rmi $(docker images -a -q)
echo "Pruning containers"
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
echo "Pruning volumes"
docker volume ls -f dangling=true
echo "---------------------------------------------"