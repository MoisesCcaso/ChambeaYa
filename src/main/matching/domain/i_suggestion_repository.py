from abc import ABC, abstractmethod


class ISuggestionRepository(ABC):
    @abstractmethod
    def save(self, suggestion):
        pass

    @abstractmethod
    def find_by_intern_id(self, intern_id):
        pass
