from typing import List, Tuple

import pytest
import pytest_asyncio

from app.usecases.interfaces.repos.challenges import IChallengesRepo
from app.usecases.interfaces.services.challange_validation import IChallengeValidation
from app.usecases.schemas.challenges import ChallengeJoinPaymentAndUsers
from app.usecases.schemas.strava import StravaAccessInDb, WebhookEvent
from tests.constants import CHALLENGE_FAILING_ACTIVITY_ID, CHALLENGE_PASSING_ACTIVITY_ID, TEST_ATHLETE_ID


@pytest_asyncio.fixture
async def test_webhook_activity() -> WebhookEvent:
    test_webhook_json = {
        "aspect_type": "create",
        "event_time": 1655410924,
        "object_id": 1,
        "object_type": "activity",
        "owner_id": TEST_ATHLETE_ID,
        "subscription_id": 218213,
        "updates": {},
    }

    return WebhookEvent(**test_webhook_json)


@pytest.mark.asyncio
async def test_validate_pass(
    challenge_validation_service: IChallengeValidation,
    linked_strava_access_and_challenge: Tuple[StravaAccessInDb, ChallengeJoinPaymentAndUsers],
    test_webhook_activity: WebhookEvent,
    challenges_repo: IChallengesRepo,
) -> None:
    """Test Case 1: Passed challenge."""

    # NOTE: The Mocked Strava client conditionally returns distances based on activity ID.
    test_webhook_activity.object_id = CHALLENGE_PASSING_ACTIVITY_ID
    # 1. Call function
    await challenge_validation_service.validate(event=test_webhook_activity)

    # 2. Given that the challenge was passed, verify that the challenge was updated to complete
    test_challenge = await challenges_repo.retrieve(id=linked_strava_access_and_challenge[1].id)

    assert test_challenge.complete


@pytest.mark.asyncio
async def test_validate_fail(
    challenge_validation_service: IChallengeValidation,
    linked_strava_access_and_challenge: Tuple[StravaAccessInDb, ChallengeJoinPaymentAndUsers],
    test_webhook_activity: WebhookEvent,
    challenges_repo: IChallengesRepo,
) -> None:
    """Test Case 2: Failed challenge."""

    # NOTE: The Mocked Strava client conditionally returns distances based on activity ID.
    test_webhook_activity.object_id = CHALLENGE_FAILING_ACTIVITY_ID
    # 1. Call function
    await challenge_validation_service.validate(event=test_webhook_activity)

    # 2. Given that the challenge was passed, verify that the challenge was updated to complete
    test_challenge = await challenges_repo.retrieve(id=linked_strava_access_and_challenge[1].id)

    assert not test_challenge.complete
