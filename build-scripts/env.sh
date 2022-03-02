echo "exporting environment variables (build-scripts) .... "

export TOPDIR=$(git rev-parse --show-toplevel)
export FULL_BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)
export CURRENT_TAG = $(git describe --abbrev=0 --tags)
if [ $FULL_BRANCH_NAME == "master"] 
then 
   export TAGNAME=$CURRENT_TAG
else
   export TAGNAME="$CURRENT_TAG-jenkins-dev-$BUILD_NUMBER" 
fi

export BUILD_COMPOSE_LIST="-f $TOPDIR/docker-compose.yml"
export TEST_COMPOSE_LIST="-f $TOPDIR/docker-compose.yml -f test/docker-compose.yml"