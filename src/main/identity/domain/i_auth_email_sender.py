from abc import ABC, abstractmethod


class IAuthEmailSender(ABC):
    @abstractmethod
    def send_activation(self, recipient, token):
        pass

    @abstractmethod
    def send_password_reset(self, recipient, token):
        pass

    @abstractmethod
    def send_test(self, recipient):
        pass
