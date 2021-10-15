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
                echo "------------------------- RUNNING ENV BUILD STAGE ON JENKINS ------------------------"
                sh 'make env'
            }
        }
        stage ('docker') {
            steps {
                echo "------------------------- RUNNING DOCKER BUILD STAGE ON JENKINS ------------------------"
                sh 'make docker'
            }
        }
        stage ('test') {
            steps {
                echo "------------------------- RUNNING TEST BUILD STAGE ON JENKINS ------------------------"
                sh 'make test'
            }
        }
        stage ('publish') {
            steps {
                echo "------------------------- RUNNING PUBLISH BUILD STAGE ON JENKINS ------------------------"
                sh 'make publish'
            }
        }
    }
    post {
        always {
            echo "---------------------- FINAL STEP OF JENKINS RUNS ALWAYS ----------------------"
        }
    }
}