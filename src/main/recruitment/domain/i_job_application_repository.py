from abc import ABC, abstractmethod


class IJobApplicationRepository(ABC):
    @abstractmethod
    def save(self, job_application):
        pass

    @abstractmethod
    def save_all(self, job_applications):
        """Saves several job applications in a single atomic transaction."""

    @abstractmethod
    def find_by_id(self, job_application_id):
        pass

    @abstractmethod
    def find_by_intern_id(self, intern_id):
        pass

    @abstractmethod
    def find_by_job_posting_id(self, job_posting_id):
        pass

    @abstractmethod
    def find_by_job_posting_and_intern(self, job_posting_id, intern_id):
        pass
