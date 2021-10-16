var expect    = require("chai").expect;
var request = require("request");
var supertest = require("supertest");
// Define host here 
var authServerUrl = process.env.AUTHSERVICEHOST 
var userServerUrl = process.env.USERSERVICEHOST 
var productServerUrl = process.env.PRODUCTSERVICEHOST 
var notificationServerUrl = process.env.NOTIFICATIONSERVICEHOST 


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