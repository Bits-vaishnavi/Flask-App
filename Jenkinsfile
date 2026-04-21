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
        stage('Build & Push Docker') {
            steps {
                script {
                    def dockerUser = "2024tm93562" 
                    def imageName = "${dockerUser}/aceest-fitness:${BUILD_NUMBER}"
                    
                    // Build the image
                    bat "docker build -t ${imageName} ."
                    
                    withCredentials([usernamePassword(credentialsId: 'docker-hub-creds', 
                                     passwordVariable: 'DOCKER_HUB_PASSWORD', 
                                     usernameVariable: 'DOCKER_HUB_USERNAME')]) {
                        bat "echo %DOCKER_HUB_PASSWORD% | docker login -u %DOCKER_HUB_USERNAME% --password-stdin"
                        bat "docker push ${imageName}"
                        bat "docker tag ${imageName} ${dockerUser}/aceest-fitness:latest"
                        bat "docker push ${dockerUser}/aceest-fitness:latest"
                    }
                }
            }
        }
        stage('Debug K8s Connection') {
            steps {
                bat "curl -k https://127.0.0.1:54933/api" 
            }
        }
        stage('Deploy to Minikube') {
            steps {
                script {
                    bat "kubectl apply -f deployment.yaml --validate=false"
                    
                    bat "kubectl rollout restart deployment/aceest-fitness"
                    
                    bat "kubectl rollout status deployment/aceest-fitness"
                }
            }
        }
    }
}