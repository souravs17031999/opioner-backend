# taskly-backend-docker-app

# Goal - Make your day productive with us

# This project is meant to maintain the backend code for the [taskly - best online task manager app](https://souravs17031999.github.io/taskly-home/).

Currently, the project is deployed using Heroku servers and all requests are served through Heroku API gateway.
Frontend of [taskly app](https://github.com/souravs17031999/taskly-home) is served through Github pages but is planned to deploy through AWS in future.

## New to [Hacktoberfest-2021](https://hacktoberfest.digitalocean.com/) ?

- Make your first PR:

* If you are adding a feature, checkout a branch name to Feature/<PR-TITLE>. Ex. "Feature/add-feature"
* If you are fixing a bug, checkout a branch name to Bugfix/<Bug-title-fix>. Ex. "Bugfix/fix-bug"
* Commit message should be following [these practices](https://chris.beams.io/posts/git-commit/).

- Your PR's will be reviewed within a week and be released on weekends with changes updated in changelog.MD

## Objective for Hacktoberfest-2021

- Add endpoints as will be discussed below.
- Convert the Flask backend into NodeJS backend for realtime processing and low latency.

## Running application locally:
  
- Clone this repo    
  `git clone git@github.com:souravs17031999/taskly-backend-docker-app.git`   
- Start docker service if not started already on your system (Install docker from [here](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04) and docker-compose from [here](https://www.digitalocean.com/community/tutorials/how-to-install-docker-compose-on-ubuntu-18-04))         
- Run all services with docker-compose from cloned project root directory. 
  `docker-compose up --build`      
- Your services should be up and running.     

### ENV VARIABLES FOR RUNNING:

- PGHOST
- PGUSER
- PGPASSWORD
- PGDATABASE
- REQUIRE_DB_INSERT
- POSTGRES_PASSWORD
- POSTGRES_DB
- POSTGRES_USER
- ALLOWED_ORIGIN_HOST_PROD
