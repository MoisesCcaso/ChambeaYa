# application/matching_application_service.py
# LAB 12 - SOLID: S (Responsabilidad Única) y D (Inversión de Dependencias)

from typing import List, Dict, Optional
from domain.matching.sugerencia import Sugerencia
from domain.matching.i_sugerencia_repository import ISugerenciaRepository
from domain.perfil.i_perfil_repository import IPerfilRepository
from domain.convocatorias.i_convocatoria_repository import IConvocatoriaRepository
from domain.matching.matching_dominio_servicio import MatchingDominioServicio


class MatchingApplicationService:
    """
    LAB 12 - SRP: Esta clase tiene la ÚNICA responsabilidad de orquestar el proceso de matching.
    No se encarga de persistencia (lo hace SugerenciaRepository) ni de notificaciones.
    
    LAB 12 - DIP: Depende de ABSTRACCIONES (interfaces), no de implementaciones concretas.
    """

    def __init__(
        self,
        sugerencia_repo: ISugerenciaRepository,  # DIP: Dependencia de interfaz
        perfil_repo: IPerfilRepository,          # DIP: Dependencia de interfaz
        convocatoria_repo: IConvocatoriaRepository  # DIP: Dependencia de interfaz
    ):
        self.sugerencia_repo = sugerencia_repo
        self.perfil_repo = perfil_repo
        self.convocatoria_repo = convocatoria_repo
        self.matching_servicio = MatchingDominioServicio()

    def recomendar_convocatorias(self, practicante_id: int, limit: int = 10) -> List[Dict]:
        """
        Orquesta el proceso de recomendación.
        """
        # 1. Obtener perfil
        perfil = self.perfil_repo.obtener_por_usuario_id(practicante_id)
        if not perfil or not perfil.habilidades:
            return []

        # 2. Obtener convocatorias activas
        convocatorias = self.convocatoria_repo.listar_activas()
        if not convocatorias:
            return []

        # 3. Generar sugerencias (delegado al servicio de dominio)
        sugerencias = self.matching_servicio.generar_sugerencias(
            practicante_id=practicante_id,
            habilidades_practicante=perfil.habilidades,
            convocatorias=convocatorias
        )

        # 4. Guardar sugerencias (responsabilidad del repositorio)
        self.sugerencia_repo.eliminar_por_practicante(practicante_id)
        sugerencias_guardadas = self.sugerencia_repo.guardar_multiples(sugerencias[:limit])

        # 5. Formatear respuesta
        return self._formatear_resultado(sugerencias_guardadas, convocatorias)

    def _formatear_resultado(self, sugerencias: List[Sugerencia], convocatorias: List) -> List[Dict]:
        """Formatea las sugerencias para la respuesta API."""
        resultado = []
        for sug in sugerencias:
            conv = next((c for c in convocatorias if c.id == sug.convocatoria_id), None)
            if conv:
                resultado.append({
                    "convocatoria": conv.to_dict(),
                    "score_match": sug.score_match,
                    "habilidades_match": sug.habilidades_match
                })
        return resultado