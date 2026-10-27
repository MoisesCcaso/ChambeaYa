from domain.convocatorias.convocatoria import Convocatoria
from domain.convocatorias.postulacion import Postulacion


class PostulacionApplicationService:
    def __init__(
        self,
        postulacion_repository=None,
        convocatoria_repository=None,
        perfil_repository=None,
        practica_repository=None,
    ):
        self.postulacion_repository = postulacion_repository
        self.convocatoria_repository = convocatoria_repository
        self.perfil_repository = perfil_repository
        self.practica_repository = practica_repository

    def apply(self, usuario_id, convocatoria_id):
        self._require_repositories()
        practicante = self.perfil_repository.find_practicante_by_user_id(usuario_id)
        if practicante is None:
            raise ValueError("Perfil de practicante no encontrado")
        if not practicante.nombres or not practicante.apellidos:
            raise ValueError("Completa tus nombres y apellidos antes de postular")

        convocatoria = self.convocatoria_repository.find_by_id(convocatoria_id)
        if convocatoria is None:
            raise ValueError("Convocatoria no encontrada")
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
            raise ValueError("Perfil de practicante no encontrado")
        return [
            (
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
            (
                postulacion,
                self.perfil_repository.find_practicante_by_id(
                    postulacion.practicante_id
                ),
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
            raise ValueError("Postulación no encontrada")
        convocatoria = self.convocatoria_repository.find_by_id(postulacion.convocatoria_id)
        if convocatoria is None:
            raise ValueError("Convocatoria no encontrada")
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
        seleccionada = self.postulacion_repository.save(postulacion)
        for otra in otras:
            if otra.id == postulacion.id:
                continue
            if otra.estado == Postulacion.ESTADO_PENDIENTE:
                otra.rechazar()
                self.postulacion_repository.save(otra)
            elif otra.estado == Postulacion.ESTADO_SELECCIONADA:
                otra.estado = Postulacion.ESTADO_RECHAZADA
                self.postulacion_repository.save(otra)
        return seleccionada

    def reject_candidate(self, empresa_id, postulacion_id):
        self._require_repositories()
        postulacion = self.postulacion_repository.find_by_id(postulacion_id)
        if postulacion is None:
            raise ValueError("Postulación no encontrada")
        self._require_owned_convocatoria(empresa_id, postulacion.convocatoria_id)
        postulacion.rechazar()
        return self.postulacion_repository.save(postulacion)

    def cancel(self, usuario_id, postulacion_id):
        self._require_repositories()
        practicante = self.perfil_repository.find_practicante_by_user_id(usuario_id)
        if practicante is None:
            raise ValueError("Perfil de practicante no encontrado")
        postulacion = self.postulacion_repository.find_by_id(postulacion_id)
        if postulacion is None:
            raise ValueError("Postulación no encontrada")
        if postulacion.practicante_id != practicante.id:
            raise ValueError("La postulación no pertenece a este practicante")
        postulacion.cancelar()
        return self.postulacion_repository.save(postulacion)

    def reconsider_candidate(self, empresa_id, postulacion_id):
        self._require_repositories()
        postulacion = self.postulacion_repository.find_by_id(postulacion_id)
        if postulacion is None:
            raise ValueError("Postulación no encontrada")
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
            raise ValueError("Convocatoria no encontrada")
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
