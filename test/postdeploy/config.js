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

try {
    const herokuGetAppsApi = "https://api.heroku.com/apps"
    const responseApps = await setHostForDeployedAppsInContext(herokuGetAppsApi)
    console.log(responseApps)
    const requiredApps = ["auth-service-prd", "cron-worker-prd", "notification-service-prd", "product-service-prd", "user-service-prd01"]
    const deployedApps = []

    for(let app of responseApps) {
        if(app.name != undefined) {
            deployedApps.push(app.name)
            if(app.name === requiredApps[0]) {
                authServerUrl = app.web_url
            } else if(app.name === requiredApps[2]) {
                notificationServerUrl = app.web_url
            } else if(app.name === requiredApps[3]) {
                productServerUrl = app.web_url
            } else if(app.name === requiredApps[4]) {
                userServerUrl = app.web_url
            }
        }
    }
    console.log("========> Searching for required apps: ", requiredApps)
    console.log("========> Found Heroku deployed apps: ", deployedApps)
} catch (err) {
    console.log("[ERROR]: Error in getting host names from Heroku API's")
    throw new Error("[ERROR][setHostForDeployedAppsInContext]: Error in getting host names from Heroku API's")
}
// ---------------------------------------------------------

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