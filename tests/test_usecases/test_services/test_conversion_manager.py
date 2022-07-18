import pytest

from app.usecases.interfaces.services.conversion_manager import IConversionManager
from app.usecases.schemas.challenges import Pace


@pytest.mark.asyncio
async def test_cm_to_miles(
    conversion_manager_service: IConversionManager,
) -> None:

    DISTANCE = 4.00743e9  # Centimeters

    miles = conversion_manager_service.cm_to_miles(distance=DISTANCE)

    assert miles == (DISTANCE / 100) / 1609.34


@pytest.mark.asyncio
async def test_cm_per_second_to_minutes_per_mile(
    conversion_manager_service: IConversionManager,
) -> None:

    TEST_PACE_INPUT = 357.63200  # Centimeters/Second
    TEST_PACE_OUTPUT_MINUTES = 7
    TEST_PACE_OUTPUT_SECONDS = 29

    minutes_per_mile = conversion_manager_service.cm_per_second_to_minutes_per_mile(
        pace=TEST_PACE_INPUT
    )

    assert isinstance(minutes_per_mile, Pace)
    assert minutes_per_mile.minutes == TEST_PACE_OUTPUT_MINUTES
    assert minutes_per_mile.seconds == TEST_PACE_OUTPUT_SECONDS
