pipeline {
    agent any
    environment {
        PYTHON_EXE = 'C:\\Users\\Vaishnavi\\AppData\\Local\\Programs\\Python\\Python313\\python.exe'
        SONAR_SERVER = 'SonarQube-Server' 
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

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv("${SONAR_SERVER}") {
                    script {
                        def scannerHome = tool 'sonar-scanner'
                        
                        bat "${scannerHome}\\bin\\sonar-scanner.bat " +
                            "-Dsonar.projectKey=ACEest-Fitness " +
                            "-Dsonar.projectName=ACEest-Fitness-Gym " +
                            "-Dsonar.sources=. " +
                            "-Dsonar.language=py " +
                            "-Dsonar.python.version=3 " +
                            "-Dsonar.python.interpreter=${PYTHON_EXE}"
                    }
                }
            }
        }

        stage("Quality Gate") {
            steps {
                timeout(time: 2, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Unit Tests') {
            steps {
                bat "${PYTHON_EXE} -m pytest"
            }
        }
    }
}