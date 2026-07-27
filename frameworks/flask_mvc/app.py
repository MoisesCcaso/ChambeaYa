# frameworks/flask_mvc/app.py
# LAB 12 - SOLID: D (Inversión de Dependencias)
# Los módulos de alto nivel dependen de abstracciones, no de implementaciones concretas.

from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from frameworks.sqlalchemy_orm.database import db
from infrastructure.sqlalchemy_usuario_repository import SQLAlchemyUsuarioRepository
from infrastructure.sqlalchemy_perfil_repository import SQLAlchemyPerfilRepository
from infrastructure.sqlalchemy_convocatoria_repository import SQLAlchemyConvocatoriaRepository
from infrastructure.sqlalchemy_postulacion_repository import SQLAlchemyPostulacionRepository
from application.usuario_application_service import UsuarioApplicationService
from application.matching_application_service import MatchingApplicationService
from presentation.matching_controller import matching_blueprint
from presentation.postulacion_controller import postulacion_blueprint
# ... otros imports


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chambeaya.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key'

    db.init_app(app)
    Migrate(app, db)
    CORS(app)

    # ============================================
    # LAB 12 - DIP: Inyección de Dependencias
    # Los servicios reciben interfaces (abstracciones),
    # no implementaciones concretas.
    # ============================================

    # Repositorios concretos (implementaciones)
    usuario_repo = SQLAlchemyUsuarioRepository(db.session)
    perfil_repo = SQLAlchemyPerfilRepository(db.session)
    convocatoria_repo = SQLAlchemyConvocatoriaRepository(db.session)
    postulacion_repo = SQLAlchemyPostulacionRepository(db.session)
    
    # Servicios de aplicación (dependen de interfaces)
    usuario_service = UsuarioApplicationService(usuario_repo)
    matching_service = MatchingApplicationService(
        sugerencia_repo=SugerenciaRepository(db.session),  # Inyección
        perfil_repo=perfil_repo,
        convocatoria_repo=convocatoria_repo
    )
    
    # Controladores (reciben servicios)
    app.register_blueprint(matching_blueprint)
    app.register_blueprint(postulacion_blueprint)
    # ... otros blueprints

    return app