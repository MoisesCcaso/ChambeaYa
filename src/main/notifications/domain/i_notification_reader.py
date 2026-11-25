from abc import ABC, abstractmethod


class INotificationReader(ABC):
    @abstractmethod
    def find_by_user_id(self, user_id):
        pass

    @abstractmethod
    def find_unread_by_user_id(self, user_id):
        pass

    @abstractmethod
    def count_unread(self, user_id):
        pass
