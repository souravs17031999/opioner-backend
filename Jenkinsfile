#!groovy

pipeline {
    agent any

    environment {
        PGHOST = credentials('PGHOST')
        PGUSER = credentials('PGUSER')
        PGPASSWORD = credentials('PGPASSWORD')
        PGDATABASE = credentials('PGDATABASE')
        REQUIRE_DB_INSERT = credentials('REQUIRE_DB_INSERT')
        POSTGRES_PASSWORD = credentials('POSTGRES_PASSWORD')
        POSTGRES_DB = credentials('POSTGRES_DB')
        POSTGRES_USER = credentials('POSTGRES_USER')
        ALLOWED_ORIGIN_HOST_PROD = credentials('ALLOWED_ORIGIN_HOST_PROD')
        dockerHubUsername = credentials('dockerHubUsername')
        dockerHubPassword = credentials('dockerHubPassword')
        BUILD_NUMBER = "${BUILD_NUMBER}"
        SLACK_WEBHOOK_URL = credentials('SLACK_WEBHOOK_URL')
        SENDGRID_API_KEY_PROD = credentials('SENDGRID_API_KEY_PROD')
        REDIS_URL = credentials('REDIS_URL')
        HEROKU_API_KEY = credentials('HEROKU_API_KEY')
    }

    stages {
        stage ('build') {
            options {
                timeout(time: 30, unit: "MINUTES")
            }
            steps {
                sh 'make build'
            }
        }
        stage ('test') {
            steps {
                sh 'make test'
            }
        }
        stage ('publish') {
            steps {
                sh 'make publish'
            }
        }
        stage ('Heroku deployment') {
            options {
                timeout(time: 30, unit: "MINUTES")
            }
            steps {
                input('Do you want to deploy to Heroku production ?')
                sh 'make heroku_deploy'
                script {
                    env.DEPLOYED="TRUE"
                }
            }
        }
        stage ('Post deploy test') {
            steps {
                script {
                    if (env.DEPLOYED == "TRUE") {
                        sh 'make test_postdeploy'
                    } 
                    else {
                        echo "Skipping Postdeploy tests"
                    }
                }
            }
        }
        stage ('clean') {
            steps {
                sh 'make clean'
            }
        }
    }
    post {
        always {
            echo "---------------------- FINAL STEP OF JENKINS RUNS ALWAYS ----------------------"
        }
    }
}