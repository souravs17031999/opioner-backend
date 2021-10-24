echo "Publishing to docker hub....."
docker login -u $dockerHubUsername -p $dockerHubPassword
export tagname=$BUILD_NUMBER
docker push souravkumardevadmin/taskly-backend:$tagname
docker-compose -f docker-compose.yml down
