from abc import ABC, abstractmethod

from app.usecases.schemas.challenges import Pace


class IConversionManager(ABC):
    @abstractmethod
    def cm_to_miles(self, distance: int) -> float:
        """Converts from centimeters to miles."""

    @abstractmethod
    def cm_per_second_to_minutes_per_mile(self, pace: int) -> Pace:
        """
        Converts from centimeters/sec to minutes/mile.
        - 100 centimeters in 1 meter
        - 1609.34 meters in 1 mile
        - 60 seconds in 1 minute
        """
