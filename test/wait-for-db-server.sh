echo "------------------------- WAITING FOR AUTH-SERVICE SERVER: /auth  -------------------------"

sleep 30

response=$(curl --write-out '%{http_code}' --silent --output /dev/null servername)
echo "------------- reponse: $response"

echo "..... SERVER WAITING TIME FINISHED ...."