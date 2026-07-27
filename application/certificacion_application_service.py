# application/certificacion_application_service.py
from typing import List, Dict, Optional
from datetime import datetime
from domain.certificacion.certificado import Certificado
from domain.certificacion.reputacion import Reputacion
from domain.certificacion.i_certificado_repository import ICertificadoRepository, IReputacionRepository
from infrastructure.sqlalchemy_practica_repository import SQLAlchemyPracticaRepository
from infrastructure.sqlalchemy_postulacion_repository import SQLAlchemyPostulacionRepository
from infrastructure.sqlalchemy_evaluacion_repository import SQLAlchemyEvaluacionRepository

class CertificacionApplicationService:
    """Servicio de aplicación para la certificación y reputación."""

    def __init__(self,
                 certificado_repo: ICertificadoRepository,
                 reputacion_repo: IReputacionRepository,
                 practica_repo: SQLAlchemyPracticaRepository,
                 postulacion_repo: SQLAlchemyPostulacionRepository,
                 evaluacion_repo: SQLAlchemyEvaluacionRepository):
        self.certificado_repo = certificado_repo
        self.reputacion_repo = reputacion_repo
        self.practica_repo = practica_repo
        self.postulacion_repo = postulacion_repo
        self.evaluacion_repo = evaluacion_repo

    def generar_certificado(self, practica_id: int) -> Certificado:
        """Genera un certificado al completar una práctica."""
        # 1. Validar práctica
        practica = self.practica_repo.obtener_por_id(practica_id)
        if not practica:
            raise ValueError("Práctica no encontrada")
        if practica.estado != 'completada':
            raise ValueError("Solo se pueden generar certificados para prácticas completadas")

        # 2. Verificar que no exista certificado
        existente = self.certificado_repo.obtener_por_practica(practica_id)
        if existente:
            raise ValueError("Ya existe un certificado para esta práctica")

        # 3. Obtener datos de la práctica y postulación
        postulacion = self.postulacion_repo.obtener_por_id(practica.postulacion_id)
        if not postulacion:
            raise ValueError("Postulación no encontrada")

        # 4. Obtener evaluaciones de la práctica
        evaluaciones = self.evaluacion_repo.obtener_por_practicante(postulacion.practicante_id)

        # 5. Crear metadatos
        metadatos = {
            "practicante_id": postulacion.practicante_id,
            "fecha_inicio": practica.fecha_inicio.isoformat() if practica.fecha_inicio else None,
            "fecha_fin": practica.fecha_fin.isoformat() if practica.fecha_fin else None,
            "horas_trabajadas": self._calcular_horas(practica.fecha_inicio, practica.fecha_fin),
            "evaluaciones": [e.to_dict() for e in evaluaciones],
            "promedio_evaluaciones": sum(e.puntaje for e in evaluaciones) / len(evaluaciones) if evaluaciones else 0
        }

        # 6. Crear certificado
        certificado = Certificado(
            id=None,
            practica_id=practica_id,
            codigo_unico=None,
            fecha_emision=datetime.utcnow(),
            estado='emitido',
            metadatos=metadatos,
            url_verificacion=f"/certificados/verificar/{None}"  # Se actualiza después
        )

        # 7. Guardar certificado
        certificado_guardado = self.certificado_repo.guardar(certificado)

        # 8. Actualizar URL de verificación
        certificado_guardado.url_verificacion = f"/certificados/verificar/{certificado_guardado.codigo_unico}"
        self.certificado_repo.actualizar(certificado_guardado)

        # 9. Actualizar reputación
        self._actualizar_reputacion(postulacion.practicante_id, metadatos['promedio_evaluaciones'])

        return certificado_guardado

    def verificar_certificado(self, codigo_unico: str) -> Dict:
        """Verifica la validez de un certificado."""
        certificado = self.certificado_repo.obtener_por_codigo(codigo_unico)
        if not certificado:
            return {"valido": False, "mensaje": "Certificado no encontrado"}

        if not certificado.es_valido():
            return {"valido": False, "mensaje": "Certificado no válido"}

        return {
            "valido": True,
            "certificado": certificado.to_dict(),
            "mensaje": "Certificado válido"
        }

    def revocar_certificado(self, certificado_id: int, motivo: str) -> Certificado:
        """Revoca un certificado."""
        certificado = self.certificado_repo.obtener_por_id(certificado_id)
        if not certificado:
            raise ValueError("Certificado no encontrado")

        certificado.revocar(motivo)
        return self.certificado_repo.actualizar(certificado)

    def obtener_certificados_practicante(self, practicante_id: int) -> List[Dict]:
        """Obtiene todos los certificados de un practicante."""
        certificados = self.certificado_repo.obtener_por_practicante(practicante_id)
        return [c.to_dict() for c in certificados]

    def obtener_reputacion(self, usuario_id: int) -> Dict:
        """Obtiene la reputación de un usuario."""
        reputacion = self.reputacion_repo.obtener_por_usuario(usuario_id)
        if not reputacion:
            # Crear reputación inicial
            reputacion = Reputacion(
                id=None,
                usuario_id=usuario_id,
                score_total=0.0,
                evaluaciones_count=0,
                practicas_completadas=0,
                promedio_puntaje=0.0,
                ultima_actualizacion=datetime.utcnow()
            )
            reputacion = self.reputacion_repo.guardar(reputacion)

        return reputacion.to_dict()

    def obtener_top_reputacion(self, limit: int = 10) -> List[Dict]:
        """Obtiene el top de practicantes por reputación."""
        reputaciones = self.reputacion_repo.obtener_top_practicantes(limit)
        return [r.to_dict() for r in reputaciones]

    def _actualizar_reputacion(self, practicante_id: int, puntaje_promedio: float) -> None:
        """Actualiza la reputación de un practicante."""
        reputacion = self.reputacion_repo.obtener_por_usuario(practicante_id)
        if not reputacion:
            reputacion = Reputacion(
                id=None,
                usuario_id=practicante_id,
                score_total=0.0,
                evaluaciones_count=0,
                practicas_completadas=0,
                promedio_puntaje=0.0,
                ultima_actualizacion=datetime.utcnow()
            )

        reputacion.incrementar_practicas_completadas()
        if puntaje_promedio > 0:
            reputacion.actualizar(puntaje_promedio)

        self.reputacion_repo.guardar(reputacion)

    def _calcular_horas(self, fecha_inicio: datetime, fecha_fin: datetime) -> float:
        """Calcula las horas trabajadas entre dos fechas."""
        if not fecha_inicio or not fecha_fin:
            return 0.0
        # Asumiendo 8 horas por día hábil
        dias = (fecha_fin - fecha_inicio).days
        return max(0, dias * 8)