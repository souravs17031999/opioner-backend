echo "Building docker image for taskly backend app ......"
docker-compose -f docker-compose.yml build

echo "Publishing to docker hub....."
docker login -u $dockerHubUsername -p $dockerHubPassword
export tagname=latest
docker push souravkumardevadmin/taskly-backend:$tagname
docker-compose -f docker-compose.yml down
