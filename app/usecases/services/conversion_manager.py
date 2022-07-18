from app.usecases.interfaces.services.conversion_manager import IConversionManager
from app.usecases.schemas.challenges import Pace


class ConversionManager(IConversionManager):
    def __init__(self):
        pass

    def cm_to_miles(self, distance: int) -> float:
        """
        Converts from centimeters to miles.
        - 100 centimeters in 1 meter
        - 1609.34 meters in 1 mile
        """

        return (distance / 100) / 1609.34

    def cm_per_second_to_minutes_per_mile(self, pace: int) -> Pace:
        """
        Converts from centimeters/sec to minutes/mile.
        - 100 centimeters in 1 meter
        - 1609.34 meters in 1 mile
        - 60 seconds in 1 minute
        """

        miles_per_minute = ((pace / 100) / 1609.34) * 60
        minutes_per_mile = 1 / miles_per_minute
        minutes_decimal = minutes_per_mile - int(minutes_per_mile)
        seconds = int(minutes_decimal * 60)

        return Pace(minutes=int(minutes_per_mile), seconds=seconds)
