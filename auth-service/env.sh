#!/bin/sh

echo "--------------- TESTING FOR REQUIRED ENV VARIABLES HERE FOR AUTH-SERVICE TASKLY ------------------"
# export REQUIRE_DB_INSERT=True 
# export REQUIRE_DB_MIGRATIONS=True

if [ -z $PGHOST ]; then 
    echo "------------------ [ERROR]: PGHOST ENV VAR NOT DEFINED"
    exit 1
elif [ -z $PGUSER ]; then 
    echo "------------------ [ERROR]: PGUSER ENV VAR NOT DEFINED"
    exit 1
elif [ -z $PGPASSWORD ]; then 
    echo "------------------ [ERROR]: PGPASSWORD ENV VAR NOT DEFINED"
    exit 1
elif [ -z $PGDATABASE ]; then 
    echo "------------------ [ERROR]: PGDATABASE ENV VAR NOT DEFINED"
    exit 1
elif [ -z $REDIS_URL ]; then 
    echo "------------------ [ERROR]: REDIS_URL ENV VAR NOT DEFINED"
    exit 1
elif [ -z $REQUIRE_DB_INSERT ]; then 
    echo "------------------ [WARNING]: REQUIRE_DB_INSERT ENV VAR NOT DEFINED, DEFAULTING TO FALSE"
    REQUIRE_DB_INSERT=FALSE
elif [ -z $REQUIRE_DB_MIGRATIONS ]; then 
    echo "------------------ [WARNING]: REQUIRE_DB_MIGRATIONS ENV VAR NOT DEFINED, DEFAULTING TO FALSE"
    REQUIRE_DB_MIGRATIONS=FALSE
elif [ -z $ALLOWED_ORIGIN_HOST_PROD ]; then 
    echo "------------------ [ERROR]: ALLOWED_ORIGIN_HOST_PROD NOT DEFINED"
    exit 1
elif [ -z $TEST_JENKINS_BUILD ]; then 
    echo "------------------ [WARNING]: TEST_JENKINS_BUILD ENV VAR NOT DEFINED"
fi