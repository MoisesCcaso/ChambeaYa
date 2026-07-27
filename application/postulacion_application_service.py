# application/postulacion_application_service.py
from typing import List, Dict, Optional
from datetime import datetime
from domain.convocatorias.postulacion import Postulacion
from domain.convocatorias.i_postulacion_repository import IPostulacionRepository
from infrastructure.sqlalchemy_convocatoria_repository import SQLAlchemyConvocatoriaRepository
from infrastructure.sqlalchemy_perfil_repository import SQLAlchemyPerfilRepository

class PostulacionApplicationService:
    """Servicio de aplicación para la gestión de postulaciones."""

    def __init__(self, 
                 postulacion_repo: IPostulacionRepository,
                 convocatoria_repo: SQLAlchemyConvocatoriaRepository,
                 perfil_repo: SQLAlchemyPerfilRepository):
        self.postulacion_repo = postulacion_repo
        self.convocatoria_repo = convocatoria_repo
        self.perfil_repo = perfil_repo

    def postularse(self, practicante_id: int, convocatoria_id: int, 
                mensaje: str = "", archivos: List[str] = None) -> Dict:
        """
        ESTILO COOKBOOK: Cada paso es una instrucción clara en la "receta" de postulación.
        """
        # Paso 1: Validar que el practicante tenga perfil
        perfil = self.perfil_repo.obtener_por_usuario_id(practicante_id)
        if not perfil:
            raise ValueError("El practicante no tiene un perfil completo")
        
        # Paso 2: Validar que la convocatoria exista y esté activa
        convocatoria = self.convocatoria_repo.obtener_por_id(convocatoria_id)
        if not convocatoria:
            raise ValueError("Convocatoria no encontrada")
        if convocatoria.estado != 'activa':
            raise ValueError("La convocatoria no está activa")
        
        # Paso 3: Validar que no haya expirado
        if convocatoria.fecha_limite_postulacion < datetime.now().date():
            raise ValueError("La convocatoria ha expirado")
        
        # Paso 4: Validar que no haya postulación duplicada
        existente = self.postulacion_repo.obtener_por_practicante_y_convocatoria(
            practicante_id, convocatoria_id
        )
        if existente:
            raise ValueError("Ya existe una postulación para esta convocatoria")
        
        # Paso 5: Crear la postulación
        postulacion = Postulacion(
            id=None,
            convocatoria_id=convocatoria_id,
            practicante_id=practicante_id,
            fecha_postulacion=datetime.utcnow(),
            estado='pendiente',
            mensaje_postulacion=mensaje,
            archivos_adjuntos=archivos or []
        )
        
        # Paso 6: Guardar
        guardada = self.postulacion_repo.guardar(postulacion)
        
        return guardada.to_dict()

    def obtener_postulaciones_practicante(self, practicante_id: int) -> List[Dict]:
        """Obtiene todas las postulaciones de un practicante."""
        postulaciones = self.postulacion_repo.obtener_por_practicante(practicante_id)
        return [p.to_dict() for p in postulaciones]

    def obtener_postulaciones_convocatoria(self, convocatoria_id: int) -> List[Dict]:
        """Obtiene todas las postulaciones de una convocatoria."""
        postulaciones = self.postulacion_repo.obtener_por_convocatoria(convocatoria_id)
        return [p.to_dict() for p in postulaciones]

    def actualizar_estado(self, postulacion_id: int, nuevo_estado: str, 
                          usuario_rol: str = "empresa") -> Dict:
        """Actualiza el estado de una postulación."""
        if usuario_rol != "empresa":
            raise PermissionError("Solo las empresas pueden cambiar el estado de postulaciones")
        
        estados_validos = ['pendiente', 'aceptada', 'rechazada', 'completada']
        if nuevo_estado not in estados_validos:
            raise ValueError(f"Estado inválido. Debe ser uno de: {estados_validos}")
        
        postulacion = self.postulacion_repo.obtener_por_id(postulacion_id)
        if not postulacion:
            raise ValueError("Postulación no encontrada")
        
        if nuevo_estado == 'aceptada':
            postulacion.aceptar()
        elif nuevo_estado == 'rechazada':
            postulacion.rechazar()
        elif nuevo_estado == 'completada':
            postulacion.completar()
        
        actualizada = self.postulacion_repo.actualizar_estado(postulacion_id, nuevo_estado)
        return actualizada.to_dict()

    def retirar_postulacion(self, postulacion_id: int, practicante_id: int) -> bool:
        """Retira una postulación (solo si está pendiente y es del practicante)."""
        postulacion = self.postulacion_repo.obtener_por_id(postulacion_id)
        if not postulacion:
            raise ValueError("Postulación no encontrada")
        if postulacion.practicante_id != practicante_id:
            raise PermissionError("No puedes retirar una postulación que no es tuya")
        if postulacion.estado != 'pendiente':
            raise ValueError(f"No se puede retirar una postulación en estado '{postulacion.estado}'")
        return self.postulacion_repo.eliminar(postulacion_id)