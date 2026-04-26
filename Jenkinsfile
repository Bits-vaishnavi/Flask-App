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

        stage('Unit Tests') {
            steps {
                bat "${PYTHON_EXE} -m pytest --cov=. --cov-report=xml"
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
                            "-Dsonar.python.coverage.reportPaths=coverage.xml " +
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
        
        stage('Deploy to Minikube (Blue-Green)') {
            steps {
                script {
                    def kConfig = "C:\\Users\\Vaishnavi\\.kube\\config"
                    def dockerUser = "2024tm93562" 
                    def imageName = "${dockerUser}/aceest-fitness:${BUILD_NUMBER}"
                    
                    // Create namespace
                    bat "kubectl --kubeconfig=${kConfig} get namespace blue-green-deployment || kubectl --kubeconfig=${kConfig} create namespace blue-green-deployment"
                    
                    // Make sure both deployments and service exist
                    bat "kubectl --kubeconfig=${kConfig} apply -f deployment-blue.yaml -n blue-green-deployment"
                    bat "kubectl --kubeconfig=${kConfig} apply -f deployment-green.yaml -n blue-green-deployment"
                    bat "kubectl --kubeconfig=${kConfig} apply -f service.yaml -n blue-green-deployment"
                    
                    // Use powershell to toggle the active color and switch traffic
                    def script = """
                    \$kConfig = "${kConfig}"
                    \$imageName = "${imageName}"
                    \$activeColor = (kubectl --kubeconfig=\$kConfig get svc fitness-service -n blue-green-deployment -o jsonpath='{.spec.selector.version}')
                    
                    if (\$activeColor -eq "green") {
                        \$targetColor = "blue"
                    } else {
                        \$targetColor = "green"
                    }
                    
                    Write-Host "Active color is \$activeColor. Deploying new image to \$targetColor..."
                    
                    kubectl --kubeconfig=\$kConfig set image deployment/aceest-fitness-\$targetColor fitness-app=\$imageName -n blue-green-deployment
                    kubectl --kubeconfig=\$kConfig rollout status deployment/aceest-fitness-\$targetColor -n blue-green-deployment
                    
                    Write-Host "Switching traffic to \$targetColor..."
                    \$patchString = '{"spec":{"selector":{"version":"' + \$targetColor + '"}}}'
                    \$patchString | Out-File -FilePath "patch.json" -Encoding ASCII
                    kubectl --kubeconfig=\$kConfig patch service fitness-service --patch-file patch.json -n blue-green-deployment
                    Write-Host "Blue-Green Deployment successful!"
                    """
                    
                    powershell script: script
                }
            }
        }
    }
}