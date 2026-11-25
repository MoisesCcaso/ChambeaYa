from recruitment.domain.convocatoria import Convocatoria
from shared.errors import DomainError

class ConvocatoriaFabrica:
    def crear_convocatoria(self, company_id, titulo, habilidades_requeridas=None, descripcion=None, beneficios=None):

        if not company_id:
            raise DomainError("La empresa es obligatoria")
        titulo = Convocatoria.normalizar_titulo(titulo)
        if habilidades_requeridas is not None:
            Convocatoria.validar_lista(habilidades_requeridas, "Las habilidades requeridas")
        if beneficios is not None:
            Convocatoria.validar_lista(beneficios, "Los beneficios")

        convocatoria = Convocatoria()
        convocatoria.company_id = company_id
        convocatoria.titulo = str(titulo).strip()
        convocatoria.descripcion = (
            str(descripcion).strip() if descripcion is not None else None
        )
        convocatoria.status = Convocatoria.ESTADO_BORRADOR
        for skill in habilidades_requeridas or []:
            convocatoria.agregar_habilidad_requerida(skill)
        for beneficio in beneficios or []:
            convocatoria.agregar_beneficio(beneficio)
        return convocatoria
