from abc import ABC, abstractmethod


class IJobPostingRepository(ABC):
    @abstractmethod
    def save(self, job_posting):
        pass

    @abstractmethod
    def find_by_id(self, job_posting_id):
        pass

    @abstractmethod
    def find_all(self):
        pass

    @abstractmethod
    def search(self, query=None, status=None):
        pass

    @abstractmethod
    def find_by_company_id(self, company_id):
        pass

    @abstractmethod
    def delete(self, job_posting_id):
        pass
