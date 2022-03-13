# Opioner-backend-docker-app

# Goal - MAKE YOUR OPINION COUNT AND SHARE WITH WORLD

# This project is meant to maintain the backend code for the [Opioner - MAKE YOUR OPINION COUNT AND SHARE WITH WORLD](https://souravs17031999.github.io/opioner-home).

Currently, the project is deployed using Heroku servers and all requests are served through Heroku API gateway.
Frontend of [Opioner app](https://github.com/souravs17031999/opioner-home) is served through Github pages but is planned to deploy through AWS in future.

## Running application locally:
  
- Clone this repo    
  `git clone git@github.com:souravs17031999/opioner-backend.git`      
- Start docker service if not started already on your system (Install docker from [here](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04) and docker-compose from [here](https://www.digitalocean.com/community/tutorials/how-to-install-docker-compose-on-ubuntu-18-04))           
- Run all services with docker-compose from cloned project root directory         
  `docker-compose up --build`      
- Your services should be up and running.  

or 

- Run `make local`

## Test the project locally:

- Run `make test`

## Test the deployed project:

- Run `make test_postdeploy` 
(useful in CI/CD pipelines)

### ENV VARIABLES FOR RUNNING (before starting the service):

- PGHOST
- PGUSER
- PGPASSWORD
- PGDATABASE
- REQUIRE_DB_INSERT
- POSTGRES_PASSWORD
- POSTGRES_DB
- POSTGRES_USER
- ALLOWED_ORIGIN_HOST_PROD
- REQUIRE_DB_MIGRATIONS
- REQUIRE_DB_INSERT
- SENDGRID_API_KEY_PROD
- FIREBASE_PROFILE_PIC_PATH
- REDIS_URL
- NOTIFICATION_INTERNAL_URL

### Microservices:

- [Auth-service](https://github.com/souravs17031999/opioner-backend/tree/master/auth-service)
- [Product-service](https://github.com/souravs17031999/opioner-backend/tree/master/product-service)
- [User-service](https://github.com/souravs17031999/opioner-backend/tree/master/user-service)
- [Notification-service](https://github.com/souravs17031999/opioner-backend/tree/master/notification-service)
- [Cron-service](https://github.com/souravs17031999/opioner-backend/tree/master/cron-service)
- Postgres
- Redis

### Deployment via CI/CD:

- Deployment pipeline follows the deployment via Heroku CI/CD docker container registries to deliver the end product.
- Tests are integrated in the pipeline (preferably Jenkins pipeline) before and after the delivery of end product to make sure we deliver the value of the product without
breaking existing functionality.

## Useful: 
- Each service is built independently using it's own Dockerfile and pushed to Heroku container registeries.
- Then, the container is released into production.
- Final built image (for every service) contains the ENTRYPOINT which starts the flask api service and runs any scripts supplied before actually starting the service.
- Every service waits for the postgres service to start first (controlled by script), as every service depends on this one.
- Repo contains db migration scripts for local setup.
  
### Notes:      
- The actual database for app will be mounted automatically at `dbdata` directory owned by docker.     
- You can use Jenkins build locally for testing your changes as it already contains `test` stage which needs to pass all the tests added.     
- For testing purpose, it will automatically create the test database in Jenkins build and will be removed after the container stops.   
- Jenkins CI/CD is already configured in Jenkinsfile and Makefile.    
- We will use dockers to deploy the app in production.   
- `dbinit` contains test data to be migrated while starting postgres container and can be used for testing.
- Currently, db migration step has been added in `auth-service`, in future it maybe be segragated.
- Currently, we have total 5 services: `auth-service`, `user-service`, `product-service`, `notification-service`, `cron-service`.  

### SRS -    
#### 1.0 Introduction   
This document aims to describe and document the software requirements specification for our product - Taskly.          

#### 1.1 Purpose
The purpose of this document is to present a detailed description of the taskly product. It will explain the purpose and features of the system, the interfaces of the system, what the system will do, the constraints under which it must operate and how the system will react to user actions.       

This document is intended for all the stakeholders who are involved directly with the product.     

#### 1.2 Scope of project       
The scope of the project is to make sure that user tasks are well managed and efficiently completed.     

We are going to create our value for the customer by making sure that user is not only creating the tasks for storing it or for just random fun but we have to make sure the user finishes the task under whatever deadline it has fixed for it.    

We need to get as real time as possible to give the user feel that we are in the user tasks together and helping it in the best way possible, at the same time not  pressurizing the user to complete the task by forcing and notifying all times at worst.     

We need to make our user feel special by making customized boards for keeping tracks of their tasks and give them options to get their notifications / reminders on whatever medium they like and at intervals they like. It will all be about customer centric and giving value to each customer by respecting their privacy and space and keeping their data secured and show whatever user wants to see according to their needs.    

#### 2.0 Overall description 
#### 2.1 Functional Requirements Specification    
Use case Login flow:    

User logins and sees whatever it has stored in the app / web (if at all earlier anything has been stored)    

User logins and sees empty screen with no tasks and only ability to add a task and we need to add a recommendation at the below of the page to keep the user engaged.    

Use case Signup flow:    

User is able to sign up itself seamlessly through following integrations and flows :     
-> username, password   
-> google sign in    
-> facebook sign in   
-> twitter sign in    

NOTE: we are not storing passwords as such in plain text or neither storing any hash. We are just encrypting and on the fly generating it, then everytime we will check and compare with the stored encrypted version.     

Use case Dashboard flow:      

User is able to very easily create a task without any hinderance    
  
User can apply push notifications for reminder through following means :    
-> email   
-> phone    

User can change the status/tag of the task → by default we can show “todo“ type tag    

We are giving user to have a option of “reminder” setting to subscribe to particular tasks and then unsubscribe to that task according to user requirement.   

CRON schedular will send reminder to all users who have reminder set for those tasks → Currently, we only send reminders once per day in the morning IST (time yet to be decided).    

#### 2.2 Non functional Requirements Specification     
Security    
-> passwords should be secure enough    
-> after logout, session should be cleared and no one should be able to see other user’s data after session is over.    

UI/UX feel - seamless experience right from login form to actual task dashboard.     
