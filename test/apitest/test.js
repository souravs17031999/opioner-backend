let config = require('./config')
let authApi = config.authApi
let userApi = config.userApi
let productApi = config.productApi
let notificationApi = config.notificationApi
let iamAPI = require('./configureKeycloak')

describe('Test Health Status of services', function() {

    let authToken;

    before('Keycloak server check', function(done) {
        
        iamAPI.getAuthUserToken()
        .then(function(access_token) {
            authToken = access_token;
            console.log("User is authenticated and logged in !")
            return done()
        }).catch(function(error) {
            console.log("Unable to check keycloak server status: ", error)
            return done(error)
        })
    })
        
    describe('/auth services api', function() {

        it('should get 200 for checking the auth service status', function(done) {
            authApi.get(`/status/health`)
            .set('Authorization', `Bearer ${authToken}`)
            .expect(200)
            .end(function(err, res) {
                if(err) {
                    console.log(err)
                    return done(err)
                }
                console.log(res.body)
                done()
            })
        })
      
    })
    
    describe('/user services api', function() {
    
        it('should get 200 for checking the user service status', function(done) {
            userApi.get(`/status/health`)
            .set('Authorization', `Bearer ${authToken}`)
            .expect(200)
            .end(function(err, res) {
                if(err) {
                    console.log(err)
                    return done(err)
                }
                console.log(res.body)
                done()
            })
        })
      
    })
    
    describe('/product services api', function() {
    
        it('should get 200 for checking the product service status', function(done) {
            productApi.get(`/status/health`)
            .set('Authorization', `Bearer ${authToken}`)
            .expect(200)
            .end(function(err, res) {
                if(err) {
                    console.log(err)
                    return done(err)
                }
                console.log(res.body)
                done()
            })
        })
      
    })
    
    describe('/notification services api', function() {
    
        it('should get 200 for checking the notification service status', function(done) {
            notificationApi.get(`/status/health`)
            .set('Authorization', `Bearer ${authToken}`)
            .expect(200)
            .end(function(err, res) {
                if(err) {
                    console.log(err)
                    return done(err)
                }
                console.log(res.body)
                done()
            })
        })
      
    })

})


