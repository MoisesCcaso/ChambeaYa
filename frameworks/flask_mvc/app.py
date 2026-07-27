# frameworks/flask_mvc/app.py
from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
import os
from dotenv import load_dotenv

from frameworks.sqlalchemy_orm.database import db
from frameworks.sqlalchemy_orm.models import *

# Importar blueprints de rutas existentes
from frameworks.flask_mvc.routes.health_routes import health_blueprint
from frameworks.flask_mvc.routes.auth_routes import auth_blueprint
from frameworks.flask_mvc.routes.perfil_routes import perfil_blueprint

# Importar nuevos blueprints de presentation
from presentation.matching_controller import matching_blueprint
from presentation.postulacion_controller import postulacion_blueprint
from presentation.practica_controller import practica_blueprint
from presentation.entregable_controller import entregable_blueprint
from presentation.certificado_controller import certificado_blueprint
from presentation.notificacion_controller import notificacion_blueprint  # <-- ESTE FALTABA
from presentation.reporte_controller import reporte_blueprint           # <-- Y ESTE TAMBIÉN

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuración
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///chambeaya.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False  # Para desarrollo local
    app.config['SESSION_PERMANENT'] = False
    
    # Inicializar extensiones
    db.init_app(app)
    Migrate(app, db)
    CORS(app, supports_credentials=True)
    
    # Registrar blueprints
    app.register_blueprint(health_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(perfil_blueprint, url_prefix='/perfil')
    app.register_blueprint(matching_blueprint)
    app.register_blueprint(postulacion_blueprint)
    app.register_blueprint(practica_blueprint)
    app.register_blueprint(entregable_blueprint)
    app.register_blueprint(certificado_blueprint)
    app.register_blueprint(notificacion_blueprint)  # <-- ESTE FALTABA
    app.register_blueprint(reporte_blueprint)        # <-- Y ESTE TAMBIÉN
    
    return app