from abc import ABC, abstractmethod


class IPracticaRepository(ABC):
    @abstractmethod
    def save(self, practica):
        pass

    @abstractmethod
    def find_by_id(self, practica_id):
        pass

    @abstractmethod
    def find_by_intern_id(self, intern_id):
        pass

    @abstractmethod
    def find_by_job_application_id(self, job_application_id):
        pass

    @abstractmethod
    def find_by_company_id(self, company_id):
        pass
