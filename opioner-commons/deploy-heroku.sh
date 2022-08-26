#!/usr/bin/env bash
set -e 

echo "Starting deployment to Heroku CI/CD....."

echo "Heroku authentication......"
HEROKU_APPS=$(HEROKU_API_KEY="${HEROKU_API_KEY}" heroku apps)
echo "Heroku container registry login......"
heroku container:login

echo "Listing heroku apps....."
echo $HEROKU_APPS

TOPDIR=$(git rev-parse --show-toplevel)

if [[ "$SKIP_TO_SCALE" == "TRUE" ]]; then
  echo "Only scaling heroku apps....."
  cd $TOPDIR/auth-service 
  heroku ps:scale web=1 -a auth-service-prd
  cd $TOPDIR/product-service 
  heroku ps:scale web=1 -a product-service-prd
  cd $TOPDIR/user-service 
  heroku ps:scale web=1 -a user-service-prd01
  cd $TOPDIR/notification-service 
  heroku ps:scale web=1 -a notification-service-prd
  cd $TOPDIR/cron-service
  heroku ps:scale worker=1 -a cron-worker-prd
  exit 0
fi

if [[ "$SKIP_TO_DELETE" == "TRUE" ]]; then
  echo "DELETING heroku apps....."
  cd $TOPDIR/auth-service 
  heroku ps:scale web=0 -a auth-service-prd
  cd $TOPDIR/product-service 
  heroku ps:scale web=0 -a product-service-prd
  cd $TOPDIR/user-service 
  heroku ps:scale web=0 -a user-service-prd01
  cd $TOPDIR/notification-service 
  heroku ps:scale web=0 -a notification-service-prd
  cd $TOPDIR/cron-service
  heroku ps:scale worker=0 -a cron-worker-prd
  exit 0
fi

if [[ "$HEROKU_APPS" =~ .*"auth-service-prd".* ]]; then
  echo "deploying opioner auth service to production ...."
  cd $TOPDIR/auth-service 
  heroku container:push web -a auth-service-prd
  heroku container:release web -a auth-service-prd
fi 

if [[ "$HEROKU_APPS" =~ .*"product-service-prd".* ]]; then
  echo "deploying opioner product service to production ...."
  cd $TOPDIR/product-service 
  heroku container:push web -a product-service-prd
  heroku container:release web -a product-service-prd
fi 

if [[ "$HEROKU_APPS" =~ .*"user-service-prd01".* ]]; then
  echo "deploying opioner user service to production ...."
  cd $TOPDIR/user-service 
  heroku container:push web -a user-service-prd01
  heroku container:release web -a user-service-prd01
fi 

if [[ "$HEROKU_APPS" =~ .*"notification-service-prd".* ]]; then
  echo "deploying opioner notification service to production ...."
  cd $TOPDIR/notification-service 
  heroku container:push web -a notification-service-prd
  heroku container:release web -a notification-service-prd
fi 

if [[ "$HEROKU_APPS" =~ .*"cron-worker-prd".* ]]; then
  echo "deploying opioner cron service to production ...."
  cd $TOPDIR/cron-service
  heroku container:push worker -a cron-worker-prd
  heroku container:release worker -a cron-worker-prd
fi 
