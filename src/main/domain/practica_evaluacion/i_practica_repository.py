from abc import ABC, abstractmethod


class IPracticaRepository(ABC):
    @abstractmethod
    def save(self, practica):
        pass

    @abstractmethod
    def find_by_id(self, practica_id):
        pass

    @abstractmethod
    def find_by_practicante_id(self, intern_id):
        pass

    @abstractmethod
    def find_by_postulacion_id(self, postulacion_id):
        pass

    @abstractmethod
    def find_by_empresa_id(self, company_id):
        pass
