from domain.certificacion.i_certificado_repository import ICertificadoRepository
from domain.certificacion.certificado import Certificado
from domain.certificacion.codigo_qr import CodigoQR
from frameworks.sqlalchemy_orm.database import db
from frameworks.sqlalchemy_orm.models.certificado_model import CertificadoModel


class SqlAlchemyCertificadoRepository(ICertificadoRepository):
    def __init__(self):
        pass

    def save(self, certificado):
        model = None
        if certificado.id is not None:
            model = db.session.get(CertificadoModel, certificado.id)

        if model is None:
            model = CertificadoModel(practica_id=certificado.practica_id)
            db.session.add(model)

        model.qr_valor = certificado.codigo_qr.valor
        model.qr_url = certificado.codigo_qr.url_verificacion
        model.hash_integridad = certificado.hash_integridad
        model.fecha_emision = certificado.fecha_emision

        db.session.commit()
        return self._to_domain(model)

    def find_by_id(self, certificado_id):
        model = db.session.get(CertificadoModel, certificado_id)
        return self._to_domain(model)

    def find_by_codigo(self, codigo):
        model = CertificadoModel.query.filter_by(qr_valor=codigo).first()
        return self._to_domain(model)

    def find_by_practica_id(self, practica_id):
        model = CertificadoModel.query.filter_by(practica_id=practica_id).first()
        return self._to_domain(model)

    def _to_domain(self, model):
        if model is None:
            return None

        qr = CodigoQR(
            valor=model.qr_valor,
            url_verificacion=model.qr_url,
        )
        return Certificado(
            id=model.id,
            practica_id=model.practica_id,
            codigo_qr=qr,
            hash_integridad=model.hash_integridad,
            fecha_emision=model.fecha_emision,
        )
