# application/matching_application_service.py
from typing import List, Dict
from domain.matching.sugerencia import Sugerencia
from domain.matching.i_sugerencia_repository import ISugerenciaRepository
from domain.matching.matching_dominio_servicio import MatchingDominioServicio
from infrastructure.sqlalchemy_perfil_repository import SQLAlchemyPerfilRepository
from infrastructure.sqlalchemy_convocatoria_repository import SQLAlchemyConvocatoriaRepository

class MatchingApplicationService:
    """Servicio de aplicación para el matching de convocatorias."""

    def __init__(self, 
                 sugerencia_repo: ISugerenciaRepository,
                 perfil_repo: SQLAlchemyPerfilRepository,
                 convocatoria_repo: SQLAlchemyConvocatoriaRepository):
        self.sugerencia_repo = sugerencia_repo
        self.perfil_repo = perfil_repo
        self.convocatoria_repo = convocatoria_repo
        self.matching_servicio = MatchingDominioServicio()

    def recomendar_convocatorias(self, practicante_id: int, limit: int = 10) -> List[Dict]:
        """
        ESTILO PIPELINE: Procesamiento en etapas secuenciales.
        Cada etapa transforma los datos y los pasa a la siguiente.
        """
        # Etapa 1: Obtener perfil del practicante
        perfil = self.perfil_repo.obtener_por_usuario_id(practicante_id)
        if not perfil or not perfil.habilidades:
            return []
        
        habilidades_practicante = perfil.habilidades
        
        # Etapa 2: Filtrar convocatorias activas
        convocatorias = self.convocatoria_repo.listar_activas()
        if not convocatorias:
            return []
        
        # Etapa 3: Calcular score de coincidencia usando Jaccard
        def calcular_match(convocatoria):
            habilidades_conv = convocatoria.habilidades_requeridas or []
            interseccion = set(habilidades_practicante) & set(habilidades_conv)
            union = set(habilidades_practicante) | set(habilidades_conv)
            score = len(interseccion) / len(union) if union else 0
            habilidades_match = list(interseccion)
            return (convocatoria, score, habilidades_match)
        
        # Etapa 4: Generar todas las coincidencias
        matches = [calcular_match(c) for c in convocatorias]
        
        # Etapa 5: Filtrar solo las que tienen score > 0
        matches = [m for m in matches if m[1] > 0]
        
        # Etapa 6: Ordenar por score descendente
        matches.sort(key=lambda x: x[1], reverse=True)
        
        # Etapa 7: Seleccionar top N y formatear respuesta
        resultado = []
        for conv, score, habilidades_match in matches[:limit]:
            resultado.append({
                "convocatoria": conv.to_dict(),
                "score_match": score,
                "habilidades_match": habilidades_match
            })
        
        return resultado

    def recomendar_practicantes(self, convocatoria_id: int, limit: int = 10) -> List[Dict]:
        """
        Genera recomendaciones de practicantes para una convocatoria.
        """
        # Obtener convocatoria
        convocatoria = self.convocatoria_repo.obtener_por_id(convocatoria_id)
        if not convocatoria:
            return []
        
        # Obtener todos los practicantes con perfil
        # Nota: Este método necesita ser implementado en el repositorio de perfiles
        # Por ahora retornamos lista vacía
        return []