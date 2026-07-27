# domain/matching/__init__.py
from .sugerencia import Sugerencia
from .resultado_matching import ResultadoMatching
from .i_sugerencia_repository import ISugerenciaRepository
from .matching_dominio_servicio import MatchingDominioServicio

__all__ = [
    'Sugerencia',
    'ResultadoMatching',
    'ISugerenciaRepository',
    'MatchingDominioServicio'
]