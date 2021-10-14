echo "-------------------- INSIDE DOCKER FLOW FILE ----------------------"
echo "--------------------- USER: "
whoami
echo "Building docker image for app ......"
docker-compose -f docker-compose.yml build
docker-compose -f docker-compose.yml down
