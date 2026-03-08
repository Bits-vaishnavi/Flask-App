pipeline {
  agent any

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Install Dependencies') {
      steps {
        sh 'python -m pip install --upgrade pip'
        sh 'pip install -r requirements.txt'
      }
    }

    stage('Lint & Syntax Check') {
      steps {
        sh 'python -m py_compile app.py'
        sh 'python -m py_compile test_app.py'
        sh 'ruff check .'
      }
    }

    stage('Unit Tests') {
      steps {
        sh 'pytest -q'
      }
    }

    stage('Build Docker Image') {
      steps {
        sh 'docker build -t aceest-fitness-api:jenkins .'
      }
    }

    stage('Smoke Test Container') {
      steps {
        sh 'docker run --rm aceest-fitness-api:jenkins python -c "import app; print(\"ok\")"'
      }
    }
  }

  post {
    always {
      junit 'test-results.xml'
    }
  }
}
