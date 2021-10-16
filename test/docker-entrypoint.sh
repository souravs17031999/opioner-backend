echo "------------------------- INSIDE DOCKER ENTRYPOINT FOR TEST -------------------------"

source wait-for-db-server.sh 

source run-tests.sh 