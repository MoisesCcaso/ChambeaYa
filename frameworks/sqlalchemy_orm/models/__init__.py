# frameworks/sqlalchemy_orm/models/__init__.py
from .usuario_model import UsuarioModel
from .practicante_model import PracticanteModel
from .empresa_model import EmpresaModel
from .convocatoria_model import ConvocatoriaModel

# Nuevos modelos
from .postulacion_model import PostulacionModel
from .sugerencia_model import SugerenciaModel
from .practica_model import PracticaModel
from .entregable_model import EntregableModel
from .evaluacion_model import EvaluacionModel
from .certificado_model import CertificadoModel
from .reputacion_model import ReputacionModel
from .notificacion_model import NotificacionModel

__all__ = [
    'UsuarioModel',
    'PracticanteModel',
    'EmpresaModel',
    'ConvocatoriaModel',
    'PostulacionModel',
    'SugerenciaModel',
    'PracticaModel',
    'EntregableModel',
    'EvaluacionModel',
    'CertificadoModel',
    'ReputacionModel',
    'NotificacionModel'
]