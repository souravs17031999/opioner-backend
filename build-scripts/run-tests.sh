echo "----------------- INNSIDE RUN TESTS FILE -------------------------"

echo "----------------- Building Docker containers for apitest ..... "

docker-compose -f test/docker-compose.yml up --build
docker-compose -f test/docker-compose.yml down