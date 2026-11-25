from abc import ABC, abstractmethod


class ICertificateRepository(ABC):
    @abstractmethod
    def save(self, certificate):
        pass

    @abstractmethod
    def find_by_id(self, certificate_id):
        pass

    @abstractmethod
    def find_by_code(self, code):
        pass

    @abstractmethod
    def find_by_internship_id(self, internship_id):
        pass
