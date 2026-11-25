from certification.domain.archivo_pdf import ArchivoPDF

class Certificado:
    def __init__(self, id=None, internship_id=None, codigo_qr=None, documento=None):
        self.id = id
        self.internship_id = internship_id
        self.codigo_qr = codigo_qr
        self.documento = documento

    def generar_pdf(self, contenido):
        self.documento = ArchivoPDF.create(self.internship_id, contenido)
        return self.documento

    def verificar_integridad(self, contenido):
        if self.documento is None:
            return False
        return self.documento.verificar_integridad(contenido)

    def verificar_qr(self, value):
        if self.codigo_qr is None:
            return False
        return self.codigo_qr.verificar(value)