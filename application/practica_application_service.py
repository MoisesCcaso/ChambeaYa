# application/practica_application_service.py
from typing import List, Dict, Optional
from datetime import datetime
from domain.practica_evaluacion.practica import Practica, EstadoPractica
from domain.practica_evaluacion.i_practica_repository import IPracticaRepository
from infrastructure.sqlalchemy_postulacion_repository import SQLAlchemyPostulacionRepository
from infrastructure.sqlalchemy_convocatoria_repository import SQLAlchemyConvocatoriaRepository

class PracticaApplicationService:
    """Servicio de aplicación para la gestión de prácticas."""

    def __init__(self, 
                 practica_repo: IPracticaRepository,
                 postulacion_repo: SQLAlchemyPostulacionRepository,
                 convocatoria_repo: SQLAlchemyConvocatoriaRepository):
        self.practica_repo = practica_repo
        self.postulacion_repo = postulacion_repo
        self.convocatoria_repo = convocatoria_repo

    def iniciar_practica(self, postulacion_id: int, datos_inicio: Dict) -> Practica:
        """Inicia una práctica a partir de una postulación aceptada."""
        # 1. Validar postulación
        postulacion = self.postulacion_repo.obtener_por_id(postulacion_id)
        if not postulacion:
            raise ValueError("Postulación no encontrada")
        if postulacion.estado != 'aceptada':
            raise ValueError("Solo se pueden iniciar prácticas de postulaciones aceptadas")
        
        # 2. Verificar que no exista práctica
        practica_existente = self.practica_repo.obtener_por_postulacion(postulacion_id)
        if practica_existente:
            raise ValueError("Ya existe una práctica para esta postulación")
        
        # 3. Verificar que el practicante no tenga otra práctica activa
        practicante_id = postulacion.practicante_id
        practicas_practicante = self.practica_repo.obtener_por_practicante(practicante_id)
        for p in practicas_practicante:
            if p.esta_activa():
                raise ValueError("El practicante ya tiene una práctica activa")
        
        # 4. Crear práctica
        practica = Practica(
            id=None,
            postulacion_id=postulacion_id,
            fecha_inicio=datetime.utcnow(),
            estado=EstadoPractica.EN_PROGRESO,
            horario_trabajo=datos_inicio.get('horario_trabajo'),
            supervisor_nombre=datos_inicio.get('supervisor_nombre'),
            supervisor_contacto=datos_inicio.get('supervisor_contacto'),
            acta_inicio_url=datos_inicio.get('acta_inicio_url')
        )
        return self.practica_repo.guardar(practica)

    def obtener_practica(self, practica_id: int) -> Optional[Practica]:
        """Obtiene una práctica por su ID."""
        return self.practica_repo.obtener_por_id(practica_id)

    def listar_practicas_practicante(self, practicante_id: int) -> List[Practica]:
        """Lista todas las prácticas de un practicante."""
        return self.practica_repo.obtener_por_practicante(practicante_id)

    def listar_practicas_empresa(self, empresa_id: int) -> List[Practica]:
        """Lista todas las prácticas de una empresa."""
        return self.practica_repo.obtener_por_empresa(empresa_id)

    def finalizar_practica(self, practica_id: int, acta_termino_url: str) -> Practica:
        """Finaliza una práctica."""
        practica = self.practica_repo.obtener_por_id(practica_id)
        if not practica:
            raise ValueError("Práctica no encontrada")
        practica.finalizar(acta_termino_url)
        return self.practica_repo.actualizar(practica)

    def cancelar_practica(self, practica_id: int) -> Practica:
        """Cancela una práctica."""
        practica = self.practica_repo.obtener_por_id(practica_id)
        if not practica:
            raise ValueError("Práctica no encontrada")
        practica.cancelar()
        return self.practica_repo.actualizar(practica)