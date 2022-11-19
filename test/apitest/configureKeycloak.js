let keycloakUrl = process.env.KEYCLOAK_SERVER_URL
let keycloakTokenUrl = keycloakUrl + "/realms/OPIONER/protocol/openid-connect/token"
let q          = require('q')

var request = require('requestretry');

var supertest = require("supertest");

var iamApi = supertest.agent(keycloakUrl)

q.longStackSupport = true // pain_during_debug--

function waitForKeycloak() {
    let deferred = q.defer()
    console.log(">>>>>>>>>>>>>>>> checking Keycloak server ")
    request({
        url: keycloakUrl,
        method: 'GET',     
        maxAttempts: 5,   // (default) try 5 times
        retryDelay: 5000,  // (default) wait for 5s before trying again
        retryStrategy: function(err, res, body) {
            console.log(">>>>>>>>>>>>>>>>> retrying !!!")
            if(res.statusCode != 200) {
                return true
            }
            return false
        }
    }, function(error, response, body){
        // this callback will only be called when the request succeeded or after maxAttempts or on error
        console.log(">>>>>>>>>>>>>> response: ", response.statusCode)
        if (error) {
            return deferred.reject(error)
        }
        if (response.statusCode >= 400) {
            return deferred.reject(response.body.message);
        }
        return deferred.resolve(body)
    });
    return deferred.promise
}

function getAuthUserToken() {

    let deferred = q.defer()
    console.log(">>>>>>>>>>>>>>>> getting Test User Auth token ")
    const requestData = {
        "client_id": "app-test-client",
        "client_secret": "FTlIovCjLL6nCU02mk7aPCZQ0wXDqHYm",
        "username": "app-test",
        "password": "3WUzX-+&h=8IV%W",
        "grant_type": "password"
    }
    request({
        url: keycloakTokenUrl,
        method: 'POST', 
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        form: requestData,   
        maxAttempts: 5,   // (default) try 5 times
        retryDelay: 5000,  // (default) wait for 5s before trying again
        retryStrategy: function(err, res, body) {
            console.log(">>>>>>>>>>>>>>>>> retrying !!!")
            if(res.statusCode != 200) {
                return true
            }
            return false
        }
    }, function(error, response, body){
        // this callback will only be called when the request succeeded or after maxAttempts or on error
        console.log(">>>>>>>>>>>>>> response: ", response.statusCode)
        if (error) {
            return deferred.reject(error)
        }
        if (response.statusCode >= 400) {
            return deferred.reject(response.body.message);
        }
        if(JSON.parse(body).access_token == undefined) {
            return deferred.reject(response.body.message);
        }
        return deferred.resolve(JSON.parse(body).access_token)
    });
    return deferred.promise

}

module.exports = {
    waitForKeycloak: waitForKeycloak,
    getAuthUserToken: getAuthUserToken
}