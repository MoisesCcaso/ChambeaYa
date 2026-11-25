from datetime import datetime, timezone
from domain.convocatorias.estado_convocatoria import estado_desde_nombre
from shared.errors import ConflictError, DomainError


class Convocatoria:
    ESTADO_BORRADOR = "borrador"
    ESTADO_PUBLICADA = "publicada"
    ESTADO_CERRADA = "cerrada"

    def __init__(
        self,
        id=None,
        company_id=None,
        titulo=None,
        descripcion=None,
        status=None,
        habilidades_requeridas=None,
        beneficios=None,
        fecha_publicacion=None,
        fecha_cierre=None,
    ):
        self.id = id
        self.company_id = company_id
        self.titulo = titulo
        self.descripcion = descripcion
        self._estado = estado_desde_nombre(status, fecha_cierre)
        self.habilidades_requeridas = habilidades_requeridas or []
        self.beneficios = beneficios or []
        self.fecha_publicacion = fecha_publicacion

    @property
    def status(self):
        return self._estado.name

    @status.setter
    def status(self, name):
        self._estado = estado_desde_nombre(name)

    @property
    def fecha_cierre(self):
        """Solo tiene valor mientras la convocatoria esta cerrada."""
        return self._estado.fecha_cierre

    def publicar(self):
        """Publica la convocatoria si está en estado borrador."""
        self._estado = self._estado.publicar()
        self.fecha_publicacion = datetime.now(timezone.utc)
        return self

    def cerrar(self):
        self._estado = self._estado.cerrar(datetime.now(timezone.utc))
        return self

    def reabrir(self):
        self._estado = self._estado.reabrir()
        self.fecha_publicacion = datetime.now(timezone.utc)
        return self

    def validar_eliminacion(self):
        if self.status != self.ESTADO_BORRADOR:
            raise ConflictError("Solo una convocatoria en borrador puede eliminarse")
        return self

    def actualizar(
        self,
        titulo=None,
        descripcion=None,
        habilidades_requeridas=None,
        beneficios=None,
    ):
        if self.status != self.ESTADO_BORRADOR:
            raise ConflictError("Solo una convocatoria en borrador puede editarse")
        if titulo is not None:
            self.titulo = self.normalizar_titulo(titulo)
        if descripcion is not None:
            self.descripcion = str(descripcion).strip()
        if habilidades_requeridas is not None:
            self.validar_lista(habilidades_requeridas, "Las habilidades requeridas")
            self.habilidades_requeridas = []
            for skill in habilidades_requeridas:
                self.agregar_habilidad_requerida(skill)
        if beneficios is not None:
            self.validar_lista(beneficios, "Los beneficios")
            self.beneficios = []
            for beneficio in beneficios:
                self.agregar_beneficio(beneficio)
        return self

    @staticmethod
    def normalizar_titulo(titulo):
        titulo_normalizado = str(titulo).strip() if titulo is not None else ""
        if not titulo_normalizado:
            raise DomainError("El título es obligatorio")
        return titulo_normalizado

    @staticmethod
    def validar_lista(values_list, name):
        if not isinstance(values_list, list):
            raise DomainError(f"{name} deben ser una lista")
        return values_list

    def agregar_habilidad_requerida(self, skill):
        normalized_skill = self._normalize_text(skill)
        if normalized_skill and normalized_skill not in self.habilidades_requeridas:
            self.habilidades_requeridas.append(normalized_skill)
        return self
    
    def agregar_beneficio(self, beneficio):
        beneficio_normalizado = self._normalize_text(beneficio)
        if beneficio_normalizado and beneficio_normalizado not in self.beneficios:
            self.beneficios.append(beneficio_normalizado)
        return self
    
    def _normalize_text(self, value):
        if value is None:
            return None
        return str(value).strip()
