#!/usr/bin/env bash

set -e 

if [[ -z $WORKSPACE ]]; then 
    TOPDIR=$(git rev-parse --show-toplevel)
    source $TOPDIR/opioner-commons/env.sh
else
    source $WORKSPACE/opioner-commons/env.sh
fi

echo " Build docker image for opioner backend app ......"
docker-compose $BUILD_COMPOSE_LIST build

# echo "Publishing to docker hub....."
# docker login -u $dockerHubUsername -p $dockerHubPassword

# echo "==================================*********==================================="
# docker tag opioner-backend_cron_service:latest souravkumardevadmin/opioner-backend_cron_service:$TAGNAME
# # docker push souravkumardevadmin/opioner-backend_cron_service:$tagname
# echo "==================================*********==================================="
# docker tag opioner-backend_notification_service:latest souravkumardevadmin/opioner-backend_notification_service:$TAGNAME
# # docker push souravkumardevadmin/taskly-backend-docker-app_notification_service:$tagname
# echo "==================================*********==================================="
# docker tag opioner-backend_product_service:latest souravkumardevadmin/opioner-backend_product_service:$TAGNAME
# # docker push souravkumardevadmin/taskly-backend-docker-app_product_service:$tagname
# echo "==================================*********==================================="
# docker tag opioner-backend_user_service:latest souravkumardevadmin/opioner-backend_user_service:$TAGNAME
# # docker push souravkumardevadmin/taskly-backend-docker-app_user_service:$tagname
# echo "==================================*********==================================="
# docker tag opioner-backend_auth_service:latest souravkumardevadmin/opioner-backend_auth_service:$TAGNAME
# # docker push souravkumardevadmin/taskly-backend-docker-app_auth_service:$tagname
# echo "==================================*********==================================="

docker-compose $BUILD_COMPOSE_LIST down


