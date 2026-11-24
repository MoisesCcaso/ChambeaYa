pipeline {
  agent any
  options { timestamps() }
  environment {
    POETRY_VIRTUALENVS_IN_PROJECT = 'true'
    APP_PORT = '5000'
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
    stage('Despliegue (servidor demo)') {
      steps {
        // fuera del workspace: cleanWs lo borraria; dontKillMe evita que Jenkins mate el servidor al terminar
        sh '''
          D="$JENKINS_HOME/chambeaya"
          mkdir -p "$D"
          if [ -f "$D/app.pid" ]; then kill "$(cat "$D/app.pid")" 2>/dev/null || true; sleep 2; fi
          rm -rf "$D/venv" "$D/demo.db"
          python3 -m venv "$D/venv"
          "$D/venv/bin/pip" install -q dist/*.whl

          export FLASK_APP=frameworks.flask_mvc.app:create_app FLASK_ENV=demo DEMO_PASSWORD=Demo1234
          export DATABASE_URL="sqlite:///$D/demo.db" SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex())')"
          # solo localhost: el modo demo tiene contrasenas conocidas y expone tokens de recuperacion
          export FLASK_PORT="$APP_PORT"
          "$D/venv/bin/flask" db upgrade
          "$D/venv/bin/flask" seed-demo

          JENKINS_NODE_COOKIE=dontKillMe setsid nohup "$D/venv/bin/chambeaya" > "$D/app.log" 2>&1 &
          echo $! > "$D/app.pid"
          for i in $(seq 30); do curl -sf "http://127.0.0.1:$APP_PORT/health" && exit 0; sleep 1; done
          cat "$D/app.log"; exit 1
        '''
      }
    }
    stage('Pruebas funcionales (Selenium)') {
      steps {
        sh '''
          CHAMBEAYA_BASE_URL="http://127.0.0.1:$APP_PORT" .poetry-venv/bin/poetry run pytest src/test/functional \
            --junitxml=reports/functional.xml --html=reports/functional.html --self-contained-html
        '''
      }
      post {
        always {
          junit 'reports/functional.xml'
          archiveArtifacts artifacts: 'reports/functional.html', allowEmptyArchive: true
        }
        // solo queda levantado si todo paso
        failure { sh 'kill "$(cat "$JENKINS_HOME/chambeaya/app.pid")" 2>/dev/null || true' }
      }
    }
  }
  post { always { cleanWs() } }
}
