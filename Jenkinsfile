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
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    sh 'make publish'
                }
            }
        }
        stage ('Heroku deployment') {
            timeout(5) {
                input {
                    id: 'userInput'
                    message "Deploy to Heroku production ?"
                    ok "Yes"
                    parameters "userInputValue"
                }
            }
            if (userInputValue == "Yes") {
                steps {
                    sh 'make heroku_deploy'
                }
            else {
                steps {
                    sh 'echo Heroku deployment'
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
            // sh "sudo chown root:souravcovenant /run/docker.sock"
        }
    }
}