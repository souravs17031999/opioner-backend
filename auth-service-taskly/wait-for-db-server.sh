echo "------------------------- WAITING FOR SERVER FOR POSTGRES DB -------------------------"

TIMEOUT=10

# while [[ $TIMEOUT -gt 0 ]]; do 
#     pg_isready -p 5432 

#     if [[ $? -eq 0 ]]; then 
#         echo
#         echo "Server ready for postgres ..... "
#         exit 0
#     fi 

#     echo -n "."
#     sleep 1 
#     TIMEOUT=$(($TIMEOUT-1)) 
# done 

sleep $TIMEOUT

echo "..... SERVER WAITING TIME FINISHED ...."