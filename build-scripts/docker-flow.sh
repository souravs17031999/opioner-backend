echo "Building docker image for taskly backend app ......"
docker-compose -f docker-compose.yml build

echo "Publishing to docker hub....."
docker login -u $dockerHubUsername -p $dockerHubPassword
export tagname=$BUILD_NUMBER

echo "==================================*********==================================="
docker tag taskly-backend-docker-app_cron_service:latest souravkumardevadmin/taskly-backend-docker-app_cron_service:$tagname
docker push souravkumardevadmin/taskly-backend-docker-app_cron_service:$tagname
echo "==================================*********==================================="
docker tag taskly-backend-docker-app_notification_service:latest souravkumardevadmin/taskly-backend-docker-app_notification_service:$tagname
docker push souravkumardevadmin/taskly-backend-docker-app_notification_service:$tagname
echo "==================================*********==================================="
docker tag taskly-backend-docker-app_product_service:latest souravkumardevadmin/taskly-backend-docker-app_product_service:$tagname
docker push souravkumardevadmin/taskly-backend-docker-app_product_service:$tagname
echo "==================================*********==================================="
docker tag taskly-backend-docker-app_user_service:latest souravkumardevadmin/taskly-backend-docker-app_user_service:$tagname
docker push souravkumardevadmin/taskly-backend-docker-app_user_service:$tagname
echo "==================================*********==================================="
docker tag taskly-backend-docker-app_auth_service:latest souravkumardevadmin/taskly-backend-docker-app_auth_service:$tagname
docker push souravkumardevadmin/taskly-backend-docker-app_auth_service:$tagname
echo "==================================*********==================================="

docker-compose -f docker-compose.yml down


