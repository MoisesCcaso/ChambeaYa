import json

from profiles.domain.i_empresa_repository import IEmpresaRepository
from profiles.domain.i_perfil_repository import IPerfilRepository
from profiles.domain.i_practicante_repository import IPracticanteRepository
from profiles.domain.practicante import Practicante
from profiles.domain.empresa import Empresa
from profiles.domain.ruc import RUC
from shared.database import db
from profiles.infrastructure.models.practicante_model import PracticanteModel
from profiles.infrastructure.models.empresa_model import EmpresaModel


class SqlAlchemyPerfilRepository(IPerfilRepository, IPracticanteRepository, IEmpresaRepository):
    def save_practicante(self, practicante):
        model = None
        if practicante.id is not None:
            model = db.session.get(PracticanteModel, practicante.id)

        if model is None:
            model = PracticanteModel.query.filter_by(user_id=practicante.user_id).first()

        if model is None:
            model = PracticanteModel(user_id=practicante.user_id)
            db.session.add(model)

        model.nombres = practicante.nombres
        model.apellidos = practicante.apellidos
        model.dni = practicante.dni
        model.carnet_universitario = practicante.carnet_universitario
        model.habilidades = self._dump_list(practicante.habilidades)
        model.formacion_educativa = self._dump_list(practicante.formacion_educativa)
        model.score_reputacion = practicante.score_reputacion
        model.identidad_verificada = practicante.identidad_verificada

        db.session.commit()
        return self._to_practicante_domain(model)

    def save_empresa(self, empresa):
        model = None
        if empresa.id is not None:
            model = db.session.get(EmpresaModel, empresa.id)

        if model is None:
            model = EmpresaModel.query.filter_by(user_id=empresa.user_id).first()

        if model is None:
            model = EmpresaModel(user_id=empresa.user_id)
            db.session.add(model)

        model.razon_social = empresa.razon_social
        model.ruc = empresa.ruc.numero if empresa.ruc else None
        model.verificada = empresa.verificada

        db.session.commit()
        return self._to_empresa_domain(model)

    def find_practicante_by_user_id(self, user_id):
        model = PracticanteModel.query.filter_by(user_id=user_id).first()
        return self._to_practicante_domain(model)
    
    def find_practicante_by_id(self, practicante_id):
        model = db.session.get(PracticanteModel, practicante_id)
        return self._to_practicante_domain(model)
    
    def find_empresa_by_user_id(self, user_id):
        model = EmpresaModel.query.filter_by(user_id=user_id).first()
        return self._to_empresa_domain(model)

    def _to_practicante_domain(self, model):
        if model is None:
            return None

        return Practicante(
            id=model.id,
            user_id=model.user_id,
            nombres=model.nombres,
            apellidos=model.apellidos,
            dni=model.dni,
            carnet_universitario=model.carnet_universitario,
            habilidades=self._load_list(model.habilidades),
            formacion_educativa=self._load_list(model.formacion_educativa),
            score_reputacion=model.score_reputacion,
            identidad_verificada=model.identidad_verificada,
        )
    
    def _to_empresa_domain(self, model):
            if model is None:
                return None

            return Empresa(
                id=model.id,
                user_id=model.user_id,
                razon_social=model.razon_social,
                ruc=RUC(numero=model.ruc) if model.ruc else None,
                verificada=model.verificada,
            )

    def _dump_list(self, values):
        return json.dumps(values or [], ensure_ascii=False)

    def _load_list(self, value):
        if not value:
            return []

        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return []

        if not isinstance(parsed, list):
            return []

        return parsed
