from abc import ABC, abstractmethod


class ICompanyRepository(ABC):
    @abstractmethod
    def save_company(self, company):
        pass

    @abstractmethod
    def find_company_by_user_id(self, user_id):
        pass
