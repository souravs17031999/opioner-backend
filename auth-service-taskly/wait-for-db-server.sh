echo "------------------------- WAITING FOR SERVER FOR POSTGRES DB STARTED -------------------------"

while ! pg_isready -h postgres
do
    echo "waiting for database to start...."
    sleep 1
done

echo "..... POSTGRES DB SERVER WAITING TIME FINISHED ...."