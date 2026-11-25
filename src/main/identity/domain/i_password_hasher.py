from abc import ABC, abstractmethod


class IPasswordHasher(ABC):
    """Domain port to hash and verify passwords."""

    @abstractmethod
    def hash(self, password):
        pass

    @abstractmethod
    def verify(self, password_hash, password):
        pass