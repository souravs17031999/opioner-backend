let config = require('./config')
let authApi = config.authApi
let userApi = config.userApi
let productApi = config.productApi
let notificationApi = config.notificationApi

describe('/auth services api', function() {

    it('should get 200 for checking the auth service status', function(done) {
        this.timeout(60000);
        authApi.get(`/status/live`)
        .expect(200)
        .end(function(err, res) {
            if(err) {
                return done(err)
            }
            done()
        })
    })
  
})

describe('/user services api', function() {

    it('should get 200 for checking the user service status', function(done) {
        this.timeout(60000);
        userApi.get(`/status/live`)
        .expect(200)
        .end(function(err, res) {
            if(err) {
                return done(err)
            }
            done()
        })
    })
  
})

describe('/product services api', function() {

    it('should get 200 for checking the product service status', function(done) {
        this.timeout(60000);
        productApi.get(`/status/live`)
        .expect(200)
        .end(function(err, res) {
            if(err) {
                return done(err)
            }
            done()
        })
    })
  
})

describe('/notification services api', function() {

    it('should get 200 for checking the notification service status', function(done) {
        this.timeout(60000);
        notificationApi.get(`/status/live`)
        .expect(200)
        .end(function(err, res) {
            if(err) {
                return done(err)
            }
            done()
        })
    })
  
})