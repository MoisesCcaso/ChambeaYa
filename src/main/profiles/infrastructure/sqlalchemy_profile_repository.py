import json

from profiles.domain.i_company_repository import ICompanyRepository
from profiles.domain.i_profile_repository import IProfileRepository
from profiles.domain.i_intern_repository import IInternRepository
from profiles.domain.intern import Intern
from profiles.domain.company import Company
from profiles.domain.ruc import RUC
from shared.database import db
from profiles.infrastructure.models.intern_model import InternModel
from profiles.infrastructure.models.company_model import CompanyModel


class SqlAlchemyProfileRepository(IProfileRepository, IInternRepository, ICompanyRepository):
    def save_intern(self, intern):
        model = None
        if intern.id is not None:
            model = db.session.get(InternModel, intern.id)

        if model is None:
            model = InternModel.query.filter_by(user_id=intern.user_id).first()

        if model is None:
            model = InternModel(user_id=intern.user_id)
            db.session.add(model)

        model.first_names = intern.first_names
        model.last_names = intern.last_names
        model.dni = intern.dni
        model.university_id_card = intern.university_id_card
        model.skills = self._dump_list(intern.skills)
        model.education = self._dump_list(intern.education)
        model.reputation_score = intern.reputation_score
        model.identity_verified = intern.identity_verified

        db.session.commit()
        return self._to_intern_domain(model)

    def save_company(self, company):
        model = None
        if company.id is not None:
            model = db.session.get(CompanyModel, company.id)

        if model is None:
            model = CompanyModel.query.filter_by(user_id=company.user_id).first()

        if model is None:
            model = CompanyModel(user_id=company.user_id)
            db.session.add(model)

        model.legal_name = company.legal_name
        model.ruc = company.ruc.number if company.ruc else None
        model.verified = company.verified

        db.session.commit()
        return self._to_company_domain(model)

    def find_intern_by_user_id(self, user_id):
        model = InternModel.query.filter_by(user_id=user_id).first()
        return self._to_intern_domain(model)
    
    def find_intern_by_id(self, intern_id):
        model = db.session.get(InternModel, intern_id)
        return self._to_intern_domain(model)
    
    def find_company_by_user_id(self, user_id):
        model = CompanyModel.query.filter_by(user_id=user_id).first()
        return self._to_company_domain(model)

    def _to_intern_domain(self, model):
        if model is None:
            return None

        return Intern(
            id=model.id,
            user_id=model.user_id,
            first_names=model.first_names,
            last_names=model.last_names,
            dni=model.dni,
            university_id_card=model.university_id_card,
            skills=self._load_list(model.skills),
            education=self._load_list(model.education),
            reputation_score=model.reputation_score,
            identity_verified=model.identity_verified,
        )
    
    def _to_company_domain(self, model):
            if model is None:
                return None

            return Company(
                id=model.id,
                user_id=model.user_id,
                legal_name=model.legal_name,
                ruc=RUC(number=model.ruc) if model.ruc else None,
                verified=model.verified,
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
