echo "-------------------- INSIDE PUBLISH FILE ----------------------"
docker-compose -f docker-compose.yml down
docker-compose -f test/docker-compose.yml down