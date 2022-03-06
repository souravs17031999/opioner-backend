#!/usr/bin/env sh

export TIMEOUT=120
export AUTH_SERVER_URL=http://auth_service:8081/auth/test

echo "------------------------- WAITING FOR AUTH-SERVICE SERVER URL: $AUTH_SERVER_URL for $TIMEOUT seconds"

export status_code=200

while [[ $TIMEOUT -gt 0 ]]; do 
    status_code=$(curl -o /dev/null -s -w "%{http_code}\n" $AUTH_SERVER_URL)
    if [[ $status_code -eq 200 ]]; then 
        echo "AUTH SERVICE SERVER READY !!"
        break
    fi
    echo "Waiting for Auth-service Server......"
    sleep 1 
    TIMEOUT=$(($TIMEOUT-1))
done

echo "..... AUTH-SERVICE SERVER WAITING TIME FINISHED ...."

if [[ $status_code -ne 200 ]]; then 
    echo "AUTH-SERVICE SERVER NOT READY !"
    exit -1
fi