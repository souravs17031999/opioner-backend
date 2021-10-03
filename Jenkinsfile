#!groovy

pipeline {
    agent any
    stages {
        stage ('Start') {
            steps {
                echo "------------------------ RUNNING START ON BUILD STAGE JENKINS ------------------"
            }
        }
        stage ('Build') {
            steps {
                echo "------------------------- RUNNING BUBILD STAGE JENKINS ------------------------"
            }
        }
    }
    post {
        always {
            echo "---------------------- FINAL STEP OF JENKINS RUNS ALWAYS ----------------------"
        }
    }
}