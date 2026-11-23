from typing import Final

from domain.convocatorias.convocatoria import Convocatoria
from domain.convocatorias.postulacion import Postulacion
from application.mensajes_error import CONVOCATORIA_NO_ENCONTRADA, POSTULACION_NO_ENCONTRADA
from application.dtos import CandidatoConvocatoriaDTO, PostulacionDetalleDTO

NOT_FOUND_PRACTICANTE: Final = "Perfil de practicante no encontrado"


class PostulacionApplicationService:
    def __init__(
        self,
        postulacion_repository=None,
        convocatoria_repository=None,
        perfil_repository=None,
        practica_repository=None,
        practicante_repository=None,
        notificacion_service=None,
    ):
        self.postulacion_repository = postulacion_repository
        self.convocatoria_repository = convocatoria_repository
        self.practicante_repository = practicante_repository or perfil_repository
        self.perfil_repository = self.practicante_repository
        self.practica_repository = practica_repository
        self.notificacion_service = notificacion_service

    def apply(self, usuario_id, convocatoria_id):
        self._require_repositories()
        practicante = self.perfil_repository.find_practicante_by_user_id(usuario_id)
        if practicante is None:
            raise ValueError(NOT_FOUND_PRACTICANTE)
        if not practicante.nombres or not practicante.apellidos:
            raise ValueError("Completa tus nombres y apellidos antes de postular")

        convocatoria = self.convocatoria_repository.find_by_id(convocatoria_id)
        if convocatoria is None:
            raise ValueError(CONVOCATORIA_NO_ENCONTRADA)
        if convocatoria.estado != Convocatoria.ESTADO_PUBLICADA:
            raise ValueError("Solo se puede postular a convocatorias publicadas")

        existente = self.postulacion_repository.find_by_convocatoria_and_practicante(
            convocatoria_id, practicante.id
        )
        if existente is not None:
            if existente.estado == Postulacion.ESTADO_CANCELADA:
                existente.reactivar()
                return self.postulacion_repository.save(existente)
            raise ValueError("Ya existe una postulación para esta convocatoria")

        return self.postulacion_repository.save(
            Postulacion(
                convocatoria_id=convocatoria_id,
                practicante_id=practicante.id,
            )
        )

    def list_for_practicante(self, usuario_id):
        self._require_repositories()
        practicante = self.perfil_repository.find_practicante_by_user_id(usuario_id)
        if practicante is None:
            raise ValueError(NOT_FOUND_PRACTICANTE)
        return [
            PostulacionDetalleDTO(
                postulacion,
                self.convocatoria_repository.find_by_id(postulacion.convocatoria_id),
            )
            for postulacion in self.postulacion_repository.find_by_practicante_id(
                practicante.id
            )
        ]

    def list_for_convocatoria(self, empresa_id, convocatoria_id):
        self._require_repositories()
        self._require_owned_convocatoria(empresa_id, convocatoria_id)
        return [
            CandidatoConvocatoriaDTO(
                postulacion,
                self.perfil_repository.find_practicante_by_id(postulacion.practicante_id),
                self.practica_repository.find_by_postulacion_id(postulacion.id),
            )
            for postulacion in self.postulacion_repository.find_by_convocatoria_id(
                convocatoria_id
            )
        ]

    def select_candidate(self, empresa_id, postulacion_id):
        self._require_repositories()
        postulacion = self.postulacion_repository.find_by_id(postulacion_id)
        if postulacion is None:
            raise ValueError(POSTULACION_NO_ENCONTRADA)
        convocatoria = self.convocatoria_repository.find_by_id(postulacion.convocatoria_id)
        if convocatoria is None:
            raise ValueError(CONVOCATORIA_NO_ENCONTRADA)
        if convocatoria.empresa_id != empresa_id:
            raise ValueError("La convocatoria no pertenece a esta empresa")

        otras = self.postulacion_repository.find_by_convocatoria_id(
            postulacion.convocatoria_id
        )
        for otra in otras:
            if (
                otra.id != postulacion.id
                and otra.estado == Postulacion.ESTADO_SELECCIONADA
                and self.practica_repository.find_by_postulacion_id(otra.id) is not None
            ):
                raise ValueError(
                    "No se puede cambiar al candidato porque la práctica seleccionada ya inició"
                )

        postulacion.seleccionar()
        modificadas = [postulacion]
        rechazadas = []
        for otra in otras:
            if otra.id == postulacion.id:
                continue
            if otra.estado == Postulacion.ESTADO_PENDIENTE:
                otra.rechazar()
                modificadas.append(otra)
                rechazadas.append(otra)
            elif otra.estado == Postulacion.ESTADO_SELECCIONADA:
                otra.rechazar_seleccionada()
                modificadas.append(otra)
                rechazadas.append(otra)
        guardadas = self.postulacion_repository.save_all(modificadas)
        seleccionada = guardadas[0]
        self._notificar_seleccion(seleccionada, rechazadas)
        return seleccionada


    def _notificar_seleccion(self, seleccionada, rechazadas):
        if self.notificacion_service is None or self.perfil_repository is None:
            return
        try:
            practicante = self.perfil_repository.find_practicante_by_id(seleccionada.practicante_id)
            if practicante and getattr(practicante, "usuario_id", None):
                self.notificacion_service.create_notification(
                    usuario_destino_id=practicante.usuario_id,
                    tipo="POSTULACION_SELECCIONADA",
                    mensaje="Has sido seleccionado para una convocatoria",
                    metadata={"postulacion_id": seleccionada.id},
                )
            for rechazada in rechazadas:
                otro = self.perfil_repository.find_practicante_by_id(rechazada.practicante_id)
                if otro and getattr(otro, "usuario_id", None):
                    self.notificacion_service.create_notification(
                        usuario_destino_id=otro.usuario_id,
                        tipo="POSTULACION_RECHAZADA",
                        mensaje="Tu postulación no fue seleccionada",
                        metadata={"postulacion_id": rechazada.id},
                    )
        except Exception:
            pass

    def reject_candidate(self, empresa_id, postulacion_id):
        self._require_repositories()
        postulacion = self.postulacion_repository.find_by_id(postulacion_id)
        if postulacion is None:
            raise ValueError(POSTULACION_NO_ENCONTRADA)
        self._require_owned_convocatoria(empresa_id, postulacion.convocatoria_id)
        postulacion.rechazar()
        return self.postulacion_repository.save(postulacion)

    def cancel(self, usuario_id, postulacion_id):
        self._require_repositories()
        practicante = self.perfil_repository.find_practicante_by_user_id(usuario_id)
        if practicante is None:
            raise ValueError(NOT_FOUND_PRACTICANTE)
        postulacion = self.postulacion_repository.find_by_id(postulacion_id)
        if postulacion is None:
            raise ValueError(POSTULACION_NO_ENCONTRADA)
        if postulacion.practicante_id != practicante.id:
            raise ValueError("La postulación no pertenece a este practicante")
        postulacion.cancelar()
        return self.postulacion_repository.save(postulacion)

    def reconsider_candidate(self, empresa_id, postulacion_id):
        self._require_repositories()
        postulacion = self.postulacion_repository.find_by_id(postulacion_id)
        if postulacion is None:
            raise ValueError(POSTULACION_NO_ENCONTRADA)
        self._require_owned_convocatoria(empresa_id, postulacion.convocatoria_id)
        if self.practica_repository.find_by_postulacion_id(postulacion.id) is not None:
            raise ValueError(
                "No se puede cambiar la decisión porque la práctica ya fue iniciada"
            )
        postulacion.reconsiderar()
        return self.postulacion_repository.save(postulacion)

    def _require_owned_convocatoria(self, empresa_id, convocatoria_id):
        convocatoria = self.convocatoria_repository.find_by_id(convocatoria_id)
        if convocatoria is None:
            raise ValueError(CONVOCATORIA_NO_ENCONTRADA)
        if convocatoria.empresa_id != empresa_id:
            raise ValueError("La convocatoria no pertenece a esta empresa")
        return convocatoria

    def _require_repositories(self):
        if (
            self.postulacion_repository is None
            or self.convocatoria_repository is None
            or self.perfil_repository is None
            or self.practica_repository is None
        ):
            raise RuntimeError("PostulacionApplicationService requiere todos sus repositorios")
