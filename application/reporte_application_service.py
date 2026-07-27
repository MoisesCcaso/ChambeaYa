# application/reporte_application_service.py
from typing import List, Dict, Any, Optional
from datetime import datetime
from infrastructure.sqlalchemy_usuario_repository import SQLAlchemyUsuarioRepository
from infrastructure.sqlalchemy_convocatoria_repository import SQLAlchemyConvocatoriaRepository
from infrastructure.sqlalchemy_postulacion_repository import SQLAlchemyPostulacionRepository
from infrastructure.sqlalchemy_practica_repository import SQLAlchemyPracticaRepository
from infrastructure.sqlalchemy_certificado_repository import SQLAlchemyReputacionRepository

class ReporteApplicationService:
    """Servicio de aplicación para la generación de reportes."""

    def __init__(self,
                 usuario_repo: SQLAlchemyUsuarioRepository,
                 convocatoria_repo: SQLAlchemyConvocatoriaRepository,
                 postulacion_repo: SQLAlchemyPostulacionRepository,
                 practica_repo: SQLAlchemyPracticaRepository,
                 reputacion_repo: SQLAlchemyReputacionRepository):
        self.usuario_repo = usuario_repo
        self.convocatoria_repo = convocatoria_repo
        self.postulacion_repo = postulacion_repo
        self.practica_repo = practica_repo
        self.reputacion_repo = reputacion_repo

    def generar_dashboard_admin(self) -> Dict[str, Any]:
        """Genera el dashboard para el administrador."""
        # Obtener totales
        total_usuarios = len(self.usuario_repo.obtener_todos())
        total_practicantes = len(self.usuario_repo.obtener_por_rol('practicante'))
        total_empresas = len(self.usuario_repo.obtener_por_rol('empresa'))

        convocatorias = self.convocatoria_repo.obtener_todos()
        total_convocatorias = len(convocatorias)
        convocatorias_activas = len([c for c in convocatorias if c.estado == 'activa'])

        postulaciones = self.postulacion_repo.obtener_todos()
        total_postulaciones = len(postulaciones)
        postulaciones_aceptadas = len([p for p in postulaciones if p.estado == 'aceptada'])

        practicas = self.practica_repo.obtener_todos()
        total_practicas = len(practicas)
        practicas_completadas = len([p for p in practicas if p.estado == 'completada'])

        return {
            "totales": {
                "usuarios": total_usuarios,
                "practicantes": total_practicantes,
                "empresas": total_empresas,
                "convocatorias": total_convocatorias,
                "convocatorias_activas": convocatorias_activas,
                "postulaciones": total_postulaciones,
                "postulaciones_aceptadas": postulaciones_aceptadas,
                "practicas": total_practicas,
                "practicas_completadas": practicas_completadas
            },
            "ratios": {
                "tasa_conversion_postulacion_a_practica": self._calcular_tasa_conversion(total_postulaciones, postulaciones_aceptadas),
                "tasa_completitud_practicas": self._calcular_tasa_conversion(total_practicas, practicas_completadas)
            }
        }

    def generar_reporte_postulaciones(self, fecha_inicio: str, fecha_fin: str,
                                      empresa_id: Optional[int] = None) -> Dict[str, Any]:
        """Genera reporte de postulaciones por período."""
        # Convertir fechas
        try:
            inicio = datetime.fromisoformat(fecha_inicio)
            fin = datetime.fromisoformat(fecha_fin)
        except ValueError:
            raise ValueError("Formato de fecha inválido. Usar ISO (YYYY-MM-DDTHH:MM:SS)")

        # Obtener postulaciones filtradas
        postulaciones = self.postulacion_repo.obtener_todos()
        postulaciones_filtradas = [
            p for p in postulaciones
            if inicio <= p.fecha_postulacion <= fin
        ]

        if empresa_id:
            # Filtrar por empresa
            convocatorias_empresa = self.convocatoria_repo.obtener_por_empresa(empresa_id)
            conv_ids = [c.id for c in convocatorias_empresa]
            postulaciones_filtradas = [p for p in postulaciones_filtradas if p.convocatoria_id in conv_ids]

        return {
            "periodo": {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin},
            "total_postulaciones": len(postulaciones_filtradas),
            "por_estado": self._agrupar_por_estado(postulaciones_filtradas),
            "postulaciones": [p.to_dict() for p in postulaciones_filtradas[:100]]
        }

    def generar_reporte_practicas(self, fecha_inicio: str, fecha_fin: str,
                                  empresa_id: Optional[int] = None) -> Dict[str, Any]:
        """Genera reporte de prácticas por período."""
        try:
            inicio = datetime.fromisoformat(fecha_inicio)
            fin = datetime.fromisoformat(fecha_fin)
        except ValueError:
            raise ValueError("Formato de fecha inválido. Usar ISO (YYYY-MM-DDTHH:MM:SS)")

        practicas = self.practica_repo.obtener_todos()
        practicas_filtradas = [
            p for p in practicas
            if inicio <= p.fecha_inicio <= fin
        ]

        if empresa_id:
            practicas_filtradas = self.practica_repo.obtener_por_empresa(empresa_id)

        return {
            "periodo": {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin},
            "total_practicas": len(practicas_filtradas),
            "por_estado": self._agrupar_por_estado_practica(practicas_filtradas),
            "practicas": [p.to_dict() for p in practicas_filtradas[:100]]
        }

    def generar_reporte_convocatorias(self, empresa_id: Optional[int] = None) -> Dict[str, Any]:
        """Genera reporte de convocatorias."""
        if empresa_id:
            convocatorias = self.convocatoria_repo.obtener_por_empresa(empresa_id)
        else:
            convocatorias = self.convocatoria_repo.obtener_todos()

        return {
            "total_convocatorias": len(convocatorias),
            "por_estado": self._agrupar_por_estado_convocatoria(convocatorias),
            "convocatorias": [c.to_dict() for c in convocatorias[:100]]
        }

    def generar_reporte_reputacion(self, limit: int = 10) -> Dict[str, Any]:
        """Genera reporte de top reputación."""
        top = self.reputacion_repo.obtener_top_practicantes(limit)
        return {
            "total": len(top),
            "top_practicantes": [r.to_dict() for r in top]
        }

    def _calcular_tasa_conversion(self, total: int, exitosos: int) -> float:
        """Calcula la tasa de conversión."""
        if total == 0:
            return 0.0
        return round((exitosos / total) * 100, 2)

    def _agrupar_por_estado(self, postulaciones) -> Dict[str, int]:
        """Agrupa postulaciones por estado."""
        estados = {}
        for p in postulaciones:
            estados[p.estado] = estados.get(p.estado, 0) + 1
        return estados

    def _agrupar_por_estado_practica(self, practicas) -> Dict[str, int]:
        """Agrupa prácticas por estado."""
        estados = {}
        for p in practicas:
            if hasattr(p, 'estado'):
                estado = p.estado.value if hasattr(p.estado, 'value') else str(p.estado)
                estados[estado] = estados.get(estado, 0) + 1
        return estados

    def _agrupar_por_estado_convocatoria(self, convocatorias) -> Dict[str, int]:
        """Agrupa convocatorias por estado."""
        estados = {}
        for c in convocatorias:
            estados[c.estado] = estados.get(c.estado, 0) + 1
        return estados