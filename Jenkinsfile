#!groovy

pipeline {
    agent any
    stages {
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
                sh 'make test'
            }
        }
    }
    post {
        always {
            echo "---------------------- FINAL STEP OF JENKINS RUNS ALWAYS ----------------------"
        }
    }
}