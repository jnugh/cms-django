pipeline {
  agent any

  stages {
    stage('Installation') {
      steps {
        sh './dev-tools/install.sh'
      }
    }
    stage('Testing') {
      parallel {
        stage('Linting') {
          steps {
            sh '. .venv/bin/activate && cd backend && pylint_runner'
          }
        }
        stage('Unit Testing') {
          steps {
            sh './dev-tools/run.sh'
            sh './dev-tools/test.sh'
            // sh 'source .venv/bin/activate'
            // sh 'export DJANGO_SETTINGS_MODULE=backend.docker_settings'
            // sh '. .venv/bin/activate && integreat-cms test cms'
          }
        }
      }
    }
    /*
    stage('Linting') {
      steps {
        sh './dev-tools/install.sh'
        sh '. .venv/bin/activate && cd backend && pylint_runner'
      }
    }*/
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
