echo "------------------------- WAITING FOR AUTH-SERVICE SERVER: /auth  -------------------------"

sleep 30

$servername=http://auth_service/auth/test
response=$(curl --write-out '%{http_code}' $servername)
echo "------------- reponse: $response"

echo "..... SERVER WAITING TIME FINISHED ...."