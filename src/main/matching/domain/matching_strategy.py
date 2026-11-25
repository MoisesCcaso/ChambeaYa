from abc import ABC, abstractmethod


class MatchingStrategy(ABC):
    """Defines the algorithm that computes skill compatibility."""

    @abstractmethod
    def calculate_compatibility(self, intern_skills, required_skills):
        """Returns the score and the matched skills."""
        raise NotImplementedError
