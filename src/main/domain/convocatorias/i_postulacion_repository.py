from abc import ABC, abstractmethod


class IPostulacionRepository(ABC):
    @abstractmethod
    def save(self, postulacion):
        pass

    @abstractmethod
    def save_all(self, postulaciones):
        """Guarda varias postulaciones en una sola transaccion atomica."""

    @abstractmethod
    def find_by_id(self, postulacion_id):
        pass

    @abstractmethod
    def find_by_practicante_id(self, practicante_id):
        pass

    @abstractmethod
    def find_by_convocatoria_id(self, convocatoria_id):
        pass

    @abstractmethod
    def find_by_convocatoria_and_practicante(self, convocatoria_id, practicante_id):
        pass
