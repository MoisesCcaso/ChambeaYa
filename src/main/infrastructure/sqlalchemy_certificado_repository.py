#!/usr/bin/python
# -*- coding: utf-8 -*-
from domain.certificacion.archivo_pdf import ArchivoPDF
from domain.certificacion.certificado import Certificado
from domain.certificacion.codigo_qr import CodigoQR
from domain.certificacion.i_certificado_repository import ICertificadoRepository
from frameworks.sqlalchemy_orm.database import db
from frameworks.sqlalchemy_orm.models.certificado_model import CertificadoModel
 
 

class SqlAlchemyCertificadoRepository(ICertificadoRepository):
    def save(self, certificado):
        model = None
        if certificado.id is not None:
            model = db.session.get(CertificadoModel, certificado.id)

        if model is None:
            model = CertificadoModel(practica_id=certificado.practica_id)
            db.session.add(model)

        if certificado.codigo_qr is not None:
            model.codigo_qr_valor = certificado.codigo_qr.valor
            model.codigo_qr_url_verificacion = certificado.codigo_qr.url_verificacion
            model.codigo_qr_hash = certificado.codigo_qr.hash_integridad

        if certificado.documento is not None:
            model.documento_url = certificado.documento.url
            model.documento_hash = certificado.documento.hash_integridad
            model.documento_contenido = certificado.documento.contenido

        db.session.commit()
        return self._to_certificado_domain(model)

    def find_by_id(self, certificado_id):
        model = db.session.get(CertificadoModel, certificado_id)
        return self._to_certificado_domain(model)

    def find_by_codigo(self, codigo_qr_valor):
        model = CertificadoModel.query.filter_by(codigo_qr_valor=codigo_qr_valor).first()
        return self._to_certificado_domain(model)

    def find_by_practica_id(self, practica_id):
        model = CertificadoModel.query.filter_by(practica_id=practica_id).first()
        return self._to_certificado_domain(model)

    def _to_certificado_domain(self, model):
        if model is None:
            return None

        codigo_qr = None
        if model.codigo_qr_valor is not None:
            codigo_qr = CodigoQR(
                valor=model.codigo_qr_valor,
                url_verificacion=model.codigo_qr_url_verificacion,
                hash_integridad=model.codigo_qr_hash,
            )

        documento = None
        if model.documento_url is not None:
            documento = ArchivoPDF(
                url=model.documento_url,
                hash_integridad=model.documento_hash,
                contenido=model.documento_contenido,
            )

        return Certificado(
            id=model.id,
            practica_id=model.practica_id,
            codigo_qr=codigo_qr,
            documento=documento,
        )
