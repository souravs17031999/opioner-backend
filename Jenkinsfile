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
        AUTHSERVICEHOST = credentials('AUTHSERVICEHOST')
        USERSERVICEHOST = credentials('USERSERVICEHOST')
        PRODUCTSERVICEHOST = credentials('PRODUCTSERVICEHOST')
        NOTIFICATIONSERVICEHOST = credentials('NOTIFICATIONSERVICEHOST')
        dockerHubUsername = credentials('dockerHubUsername')
        dockerHubPassword = credentials('dockerHubPassword')
        BUILD_NUMBER = "${BUILD_NUMBER}"
        SLACK_WEBHOOK_URL = credentials('SLACK_WEBHOOK_URL')
        SENDGRID_API_KEY_PROD = credentials('SENDGRID_API_KEY_PROD')
    }

    stages {
        stage ('permission') {
            steps {
                echo "------------------------- Fixing permissions BUILD STAGE ON JENKINS ------------------------"
                sh "sudo chown root:jenkins /run/docker.sock"
            }
        }
        stage ('env') {
            steps {
                sh 'make env'
            }
        }
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
                sh 'make publish'
            }
        }
    }
    post {
        always {
            echo "---------------------- FINAL STEP OF JENKINS RUNS ALWAYS ----------------------"
            sh "sudo chown root:souravcovenant /run/docker.sock"
        }
    }
}