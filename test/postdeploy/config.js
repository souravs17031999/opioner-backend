var expect    = require("chai").expect;
var supertest = require("supertest");
var request = require('request');
var authServerUrl, userServerUrl, productServerUrl, notificationServerUrl;

// Find host here 
// ---------------------------------------------------------
async function setHostForDeployedAppsInContext(herokuGetAppsApi) {
	return new Promise((resolve, reject) => {
		request.get({
			url: herokuGetAppsApi,
			json: true,
			headers: { 
                'Accept': 'application/vnd.heroku+json; version=3',
                'Authorization': 'Bearer ' + process.env.HEROKU_API_KEY
            },
		}, (error, response, data) => {
			if (error) {
				reject(error);
			} else if (response.statusCode !== 200) {
				reject(new Error(`Error HTTP ${response.statusCode}`));
			} else {
				resolve(data);
			}
		});
	});
}

// ---------------------------------------------------------
const requiredApps = ["auth-service-prd", "cron-worker-prd", "notification-service-prd", "product-service-prd", "user-service-prd01"]
authServerUrl = "https://" + requiredApps[0] + ".herokuapp.com/auth"
userServerUrl = "https://" + requiredApps[4] + ".herokuapp.com/user"
productServerUrl = "https://" + requiredApps[3] + ".herokuapp.com/product"
notificationServerUrl = "https://" + requiredApps[2] + ".herokuapp.com/notification"

if(authServerUrl === undefined) {
    throw new Error("AUTHSERVICEHOST NOT DEFINED IN ENVIRONMENT")
}

if(userServerUrl === undefined) {
    throw new Error("USERSERVICEHOST NOT DEFINED IN ENVIRONMENT")
}

if(productServerUrl === undefined) {
    throw new Error("PRODUCTSERVICEHOST NOT DEFINED IN ENVIRONMENT")
}

if(notificationServerUrl === undefined) {
    throw new Error("NOTIFICATIONSERVICEHOST NOT DEFINED IN ENVIRONMENT")
}

console.log("=========== AUTHSERVICEHOST: ", authServerUrl)
console.log("=========== USERSERVICEHOST: ", userServerUrl)
console.log("=========== PRODUCTSERVICEHOST: ", productServerUrl)
console.log("=========== NOTIFICATIONSERVICEHOST: ", notificationServerUrl)

var authApi = supertest.agent(authServerUrl);
var userApi = supertest.agent(userServerUrl);
var productApi = supertest.agent(productServerUrl);
var notificationApi = supertest.agent(notificationServerUrl);


module.exports = {
    authApi: authApi, 
    userApi: userApi, 
    productApi: productApi, 
    notificationApi: notificationApi
}