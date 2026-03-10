pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Check Python') {
            steps {
                bat 'python --version'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'python -m pip install --upgrade pip'
                bat 'pip install -r requirements.txt'
            }
        }

        stage('Lint & Syntax Check') {
            steps {
                bat 'python -m py_compile app.py'
            }
        }

        stage('Unit Tests') {
            steps {
                bat 'pytest'
            }
        }
    }
}
