#!/usr/bin/env sh

echo "------------------------- WAITING FOR SERVER FOR POSTGRES DB STARTED -------------------------"

while ! pg_isready -h $PGHOST -p $PGPORT
do
    echo "waiting for database to start...."
    sleep 1
done

echo "..... POSTGRES DB SERVER WAITING TIME FINISHED ...."