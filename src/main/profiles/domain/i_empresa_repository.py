from abc import ABC, abstractmethod


class IEmpresaRepository(ABC):
    @abstractmethod
    def save_empresa(self, empresa):
        pass

    @abstractmethod
    def find_empresa_by_user_id(self, user_id):
        pass
