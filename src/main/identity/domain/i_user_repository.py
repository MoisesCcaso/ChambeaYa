from abc import ABC, abstractmethod


class IUserRepository(ABC):
    @abstractmethod
    def save(self, user):
        pass

    @abstractmethod
    def find_by_email(self, email):
        pass

    @abstractmethod
    def find_by_id(self, user_id):
        pass

    @abstractmethod
    def find_by_activation_token(self, token):
        pass

    @abstractmethod
    def find_by_password_reset_token(self, token):
        pass
