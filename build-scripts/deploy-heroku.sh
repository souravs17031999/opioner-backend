echo "Starting deployment to Heroku CI/CD....."

echo "Heroku authentication......"
HEROKU_APPS=$(HEROKU_API_KEY="${HEROKU_API_KEY}" heroku apps)
echo "Heroku container registry login......"
heroku container:login

echo "Listing heroku apps....."
echo $HEROKU_APPS

TOPDIR=$(git rev-parse --show-toplevel)

if [[ "auth" =~ .*"$HEROKU_APPS".* ]]; then
  echo "deploying auth service to production ...."
  cd $TOPDIR/auth-service 
  heroku container:push web -a auth-service-prd
  heroku container:release web -a auth-service-prd
fi 

if [[ "product" =~ .*"$HEROKU_APPS".* ]]; then
  echo "deploying product service to production ...."
  cd $TOPDIR/product-service 
  heroku container:push web -a product-service-prd
  heroku container:release web -a product-service-prd
fi 

if [[ "user" =~ .*"$HEROKU_APPS".* ]]; then
  echo "deploying user service to production ...."
  cd $TOPDIR/user-service 
  heroku container:push web -a user-service-prd01
  heroku container:release web -a user-service-prd01
fi 

if [[ "notification" =~ .*"$HEROKU_APPS".* ]]; then
  echo "deploying notification service to production ...."
  cd $TOPDIR/notification-service 
  heroku container:push web -a notification-service-prd
  heroku container:release web -a notification-service-prd
fi 

if [[ "cron" =~ .*"$HEROKU_APPS".* ]]; then
  echo "deploying cron service to production ...."
  cd $TOPDIR/cron-service
  heroku container:push web -a cron-worker-prd
  heroku container:release web -a cron-worker-prd
fi 
