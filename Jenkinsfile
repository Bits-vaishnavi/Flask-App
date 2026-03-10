pipeline {
    agent any
    environment {
        
        PYTHON_EXE = 'C:\\Users\\Vaishnavi\\AppData\\Local\\Programs\\Python\\Python313\\python.exe'
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Check Python') {
            steps {
               bat "${PYTHON_EXE} --version"
            }
        }

        stage('Install Dependencies') {
            steps {
                
                bat "${PYTHON_EXE} -m pip install --upgrade pip"
                bat "${PYTHON_EXE} -m pip install -r requirements.txt"
            }
        }

        stage('Lint & Syntax Check') {
            steps {
                
                bat "${PYTHON_EXE} -m py_compile app.py"
            }
        }

        stage('Unit Tests') {
            steps {
                
                bat "${PYTHON_EXE} -m pytest"
            }
        }
    }
}