# application/postulacion_application_service.py
# LAB 12 - SOLID: S (Responsabilidad Única) y D (Inversión de Dependencias)

from typing import List, Dict, Optional
from datetime import datetime
from domain.convocatorias.postulacion import Postulacion
from domain.convocatorias.i_postulacion_repository import IPostulacionRepository
from domain.convocatorias.i_convocatoria_repository import IConvocatoriaRepository
from domain.perfil.i_perfil_repository import IPerfilRepository


class PostulacionApplicationService:
    """
    LAB 12 - SRP: Esta clase tiene la ÚNICA responsabilidad de gestionar postulaciones.
    No contiene lógica de validación compleja (delegada al dominio) ni de persistencia directa.
    
    LAB 12 - DIP: Depende de ABSTRACCIONES (interfaces), no de implementaciones concretas.
    """

    def __init__(
        self,
        postulacion_repo: IPostulacionRepository,  # DIP: Dependencia de interfaz
        convocatoria_repo: IConvocatoriaRepository,  # DIP: Dependencia de interfaz
        perfil_repo: IPerfilRepository  # DIP: Dependencia de interfaz
    ):
        self.postulacion_repo = postulacion_repo
        self.convocatoria_repo = convocatoria_repo
        self.perfil_repo = perfil_repo

    def postularse(
        self,
        practicante_id: int,
        convocatoria_id: int,
        mensaje: str = "",
        archivos: List[str] = None
    ) -> Dict:
        """
        Crea una nueva postulación.
        """
        # 1. Validar que exista el perfil
        perfil = self.perfil_repo.obtener_por_usuario_id(practicante_id)
        if not perfil:
            raise ValueError("El practicante no tiene un perfil completo")

        # 2. Validar convocatoria (delegado al dominio)
        convocatoria = self.convocatoria_repo.obtener_por_id(convocatoria_id)
        if not convocatoria:
            raise ValueError("Convocatoria no encontrada")
        if not convocatoria.esta_activa():
            raise ValueError("La convocatoria no está activa")

        # 3. Validar postulación duplicada
        existente = self.postulacion_repo.obtener_por_practicante_y_convocatoria(
            practicante_id, convocatoria_id
        )
        if existente:
            raise ValueError("Ya existe una postulación para esta convocatoria")

        # 4. Crear postulación (entidad de dominio)
        postulacion = Postulacion(
            id=None,
            convocatoria_id=convocatoria_id,
            practicante_id=practicante_id,
            fecha_postulacion=datetime.utcnow(),
            estado='pendiente',
            mensaje_postulacion=mensaje,
            archivos_adjuntos=archivos or []
        )

        # 5. Guardar (responsabilidad del repositorio)
        guardada = self.postulacion_repo.guardar(postulacion)
        return guardada.to_dict()

    def obtener_postulaciones_practicante(self, practicante_id: int) -> List[Dict]:
        """Obtiene todas las postulaciones de un practicante."""
        postulaciones = self.postulacion_repo.obtener_por_practicante(practicante_id)
        return [p.to_dict() for p in postulaciones]

    def actualizar_estado(self, postulacion_id: int, nuevo_estado: str, usuario_rol: str = "empresa") -> Dict:
        """Actualiza el estado de una postulación."""
        if usuario_rol != "empresa":
            raise PermissionError("Solo las empresas pueden cambiar el estado de postulaciones")

        estados_validos = ['pendiente', 'aceptada', 'rechazada', 'completada']
        if nuevo_estado not in estados_validos:
            raise ValueError(f"Estado inválido. Debe ser uno de: {estados_validos}")

        postulacion = self.postulacion_repo.obtener_por_id(postulacion_id)
        if not postulacion:
            raise ValueError("Postulación no encontrada")

        # La lógica de cambio de estado está en la entidad (dominio)
        if nuevo_estado == 'aceptada':
            postulacion.aceptar()
        elif nuevo_estado == 'rechazada':
            postulacion.rechazar()
        elif nuevo_estado == 'completada':
            postulacion.completar()

        actualizada = self.postulacion_repo.actualizar_estado(postulacion_id, nuevo_estado)
        return actualizada.to_dict()