from abc import ABC, abstractmethod


class IInternRepository(ABC):
    @abstractmethod
    def save_intern(self, intern):
        pass

    @abstractmethod
    def find_intern_by_user_id(self, user_id):
        pass

    @abstractmethod
    def find_intern_by_id(self, intern_id):
        pass
