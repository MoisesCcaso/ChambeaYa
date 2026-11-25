from abc import ABC, abstractmethod


class IInternshipRepository(ABC):
    @abstractmethod
    def save(self, internship):
        pass

    @abstractmethod
    def find_by_id(self, internship_id):
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
