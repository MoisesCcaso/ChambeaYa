from abc import ABC, abstractmethod


class ICertificadoRepository(ABC):
    @abstractmethod
    def save(self, certificado):
        pass

    @abstractmethod
    def find_by_id(self, certificado_id):
        pass

    @abstractmethod
    def find_by_codigo(self, codigo):
        pass

    @abstractmethod
    def find_by_practica_id(self, practica_id):
        pass
