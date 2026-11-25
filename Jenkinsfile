pipeline {
  agent any
  // un build a la vez: staging y servidor usan puertos fijos
  options { timestamps(); disableConcurrentBuilds() }
  environment {
    POETRY_VIRTUALENVS_IN_PROJECT = 'true'
    // API REST y cliente (vistas) en procesos y puertos distintos
    APP_PORT = '5000'
    APP_CLIENT_PORT = '5003'
    STAGING_PORT = '5001'
    STAGING_CLIENT_PORT = '5002'
  }
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
        // las funcionales (Selenium) corren despues, contra el staging
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
    stage('Staging efimero') {
      // instancia desechable con BD nueva dentro del workspace: las pruebas no tocan el servidor real
      steps { sh 'sh scripts/ci/deploy.sh "$WORKSPACE/.staging" "$STAGING_PORT" "$STAGING_CLIENT_PORT"' }
    }
    stage('Pruebas funcionales (Selenium)') {
      steps {
        sh '''
          CHAMBEAYA_BASE_URL="http://127.0.0.1:$STAGING_CLIENT_PORT" CHAMBEAYA_API_URL="http://127.0.0.1:$STAGING_PORT" \
            .poetry-venv/bin/poetry run pytest src/test/functional \
            --junitxml=reports/functional.xml --html=reports/functional.html --self-contained-html
        '''
      }
      post {
        always {
          junit 'reports/functional.xml'
          archiveArtifacts artifacts: 'reports/functional.html', allowEmptyArchive: true
          sh 'for f in app client; do kill "$(cat "$WORKSPACE/.staging/$f.pid")" 2>/dev/null || true; done'
        }
      }
    }
    stage('Despliegue') {
      // solo se llega aqui si todo lo anterior paso; fuera del workspace para sobrevivir a cleanWs
      steps { sh 'sh scripts/ci/deploy.sh "$JENKINS_HOME/chambeaya" "$APP_PORT" "$APP_CLIENT_PORT"' }
    }
  }
  post { always { cleanWs() } }
}
