#!/usr/bin/env sh

export TIMEOUT=120

echo "------------------------- WAITING FOR KEYCLOAK_SERVER_URL SERVER URL: $KEYCLOAK_SERVER_URL for $TIMEOUT seconds"

export status_code=200

while [[ $TIMEOUT -gt 0 ]]; do 
    status_code=$(curl -Lo /dev/null -s -w "%{http_code}\n" $KEYCLOAK_SERVER_URL)
    if [[ $status_code -eq 200 ]]; then 
        echo "KEYCLOAK_SERVER_URL SERVER READY !!"
        break
    fi
    echo "Waiting for KEYCLOAK_SERVER_URL Server......"
    sleep 1 
    TIMEOUT=$(($TIMEOUT-1))
done

echo "..... KEYCLOAK_SERVER_URL SERVER WAITING TIME FINISHED ...."

if [[ $status_code -ne 200 ]]; then 
    echo "KEYCLOAK_SERVER_URL SERVER NOT READY !"
    exit -1
fi