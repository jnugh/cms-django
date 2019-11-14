pipeline {
  agent any

  stages {
    stage('Test') {
      parallel {
        stage('Linting') {
          steps {
            sh './dev-tools/install.sh'
            sh '. .venv/bin/activate && cd backend && pylint_runner'
          }
        }
        /*stage('Unit Testing') {
          steps {
            sh './dev-tools/install.sh'
            sh './dev-tools/test.sh'
          }
        }*/
      }
    }
    stage('Packaging') {
      steps {
        sh './dev-tools/install.sh'
        sh '. .venv/bin/activate && pip3 install stdeb'
        sh '. .venv/bin/activate && python3 setup.py --command-packages=stdeb.command bdist_deb'
      }
    }
  }

  post {
    always {
        cleanWs()
    }
  }
}
