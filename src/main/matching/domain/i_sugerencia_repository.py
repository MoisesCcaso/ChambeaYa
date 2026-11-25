from abc import ABC, abstractmethod


class ISugerenciaRepository(ABC):
    @abstractmethod
    def save(self, sugerencia):
        pass

    @abstractmethod
    def find_by_intern_id(self, intern_id):
        pass
