pipeline {
  agent any
  options { timestamps() }
  environment { POETRY_VIRTUALENVS_IN_PROJECT = 'true' }
  stages {
    stage('Build (Poetry)') {
      steps {
        // Poetry dentro del workspace: misma version que poetry.lock, sin instalar nada para el usuario jenkins
        sh '''
          python3 -m venv .poetry-venv
          .poetry-venv/bin/pip install -q "poetry==2.4.3"
          .poetry-venv/bin/poetry install --no-interaction
          .poetry-venv/bin/poetry build
        '''
      }
      post { success { archiveArtifacts artifacts: 'dist/*', fingerprint: true } }
    }
    stage('Pruebas unitarias (pytest)') {
      steps {
        // las funcionales (Selenium) necesitan la app levantada y Chrome: quedan fuera del CI
        sh '.poetry-venv/bin/poetry run pytest --ignore=src/test/functional --junitxml=reports/junit.xml --cov --cov-report=xml'
      }
      post { always { junit 'reports/junit.xml' } }
    }
    stage('Analisis SonarQube') {
      steps {
        script {
          def scanner = tool 'sonar-scanner'
          withSonarQubeEnv('SonarQube') { sh "${scanner}/bin/sonar-scanner" }
        }
      }
    }
    stage('Quality Gate') {
      steps { timeout(time: 5, unit: 'MINUTES') { waitForQualityGate abortPipeline: true } }
    }
  }
  post { always { cleanWs() } }
}
