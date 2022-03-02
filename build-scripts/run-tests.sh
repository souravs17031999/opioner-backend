echo "----------------- Building Docker containers for apitest ..... "

docker-compose $TEST_COMPOSE_LIST up --build --abort-on-container-exit
docker-compose $TEST_COMPOSE_LIST down -v