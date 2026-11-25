from abc import ABC, abstractmethod


class INotificationWriter(ABC):
    @abstractmethod
    def save(self, notification):
        pass

    @abstractmethod
    def mark_as_read(self, user_id, notification_id):
        pass

    @abstractmethod
    def mark_all_as_read(self, user_id):
        pass
