import os
from typing import Any, Mapping, Tuple

import pytest
import pytest_asyncio
from databases import Database
from httpx import AsyncClient

from app.usecases.schemas.challenges import ChallengeJoinPayment, ChallengeJoinPaymentAndUsers
from app.usecases.schemas.strava import StravaAccessInDb, WebhookVerificationResponse
from app.usecases.schemas.users import UserInDb
from tests.constants import CHALLENGE_FAILING_ACTIVITY_ID, CHALLENGE_FAILING_DISTANCE, CHALLENGE_PASSING_ACTIVITY_ID, TEST_ATHLETE_ID


@pytest_asyncio.fixture
async def webhook_activity_event_json() -> Mapping[str, Any]:
    return {
        "aspect_type": "create",
        "event_time": 1655410924,
        "object_id": None,
        "object_type": "activity",
        "owner_id": TEST_ATHLETE_ID,
        "subscription_id": 218213,
        "updates": {},
    }


@pytest_asyncio.fixture
async def webhook_athlete_event_json() -> Mapping[str, Any]:
    return {
        "aspect_type": "update",
        "event_time": 1655410924,
        "object_id": 104459479,
        "object_type": "athlete",
        "owner_id": TEST_ATHLETE_ID,
        "subscription_id": 218213,
        "updates": {"authorized": "false"},
    }


@pytest.mark.asyncio
async def test_receive_webhook_challenge_pass(
    test_client: AsyncClient,
    webhook_activity_event_json: Mapping[str, Any],
    test_db: Database,
    linked_strava_access_and_challenge: Tuple[StravaAccessInDb, ChallengeJoinPaymentAndUsers],
) -> None:
    """Test Case 1: Challenge passed."""

    endpoint = "/vendors/strava/webhook"

    # NOTE: The Mocked Strava client conditionally returns distances based on activity ID.
    webhook_activity_event_json["object_id"] = CHALLENGE_PASSING_ACTIVITY_ID
    response = await test_client.post(endpoint, json=webhook_activity_event_json)
    
    test_challenge = await test_db.fetch_one(
        "SELECT * FROM challenges WHERE id=:id",
        {
            "id": linked_strava_access_and_challenge[1].id,
        },
    )
    assert response.status_code == 200
    assert test_challenge["complete"]


@pytest.mark.asyncio
async def test_receive_webhook_challenge_fail(
    test_client: AsyncClient,
    webhook_activity_event_json: Mapping[str, Any],
    test_db: Database,
    linked_strava_access_and_challenge: Tuple[StravaAccessInDb, ChallengeJoinPaymentAndUsers],
) -> None:
    """Test Case 2: Challenge failed."""

    endpoint = "/vendors/strava/webhook"

    # NOTE: The Mocked Strava client conditionally returns distances based on activity ID.
    webhook_activity_event_json["object_id"] = CHALLENGE_FAILING_ACTIVITY_ID
    response = await test_client.post(endpoint, json=webhook_activity_event_json)
    
    test_challenge = await test_db.fetch_one(
        "SELECT * FROM challenges WHERE id=:id",
        {
            "id": linked_strava_access_and_challenge[1].id,
        },
    )
    assert response.status_code == 200
    assert not test_challenge["complete"]


@pytest.mark.asyncio
async def test_receive_webhook_revoked_access(
    test_client: AsyncClient,
    webhook_athlete_event_json: Mapping[str, Any],
    test_db: Database,
    linked_strava_access_and_challenge: Tuple[StravaAccessInDb, ChallengeJoinPaymentAndUsers],
) -> None:
    """Test Case 3: User revoked access to his or her Strava account."""

    endpoint = "/vendors/strava/webhook"

    response = await test_client.post(endpoint, json=webhook_athlete_event_json)

    test_saved_strava_access_obj = await test_db.fetch_one(
        "SELECT * FROM strava_access WHERE athlete_id=:athlete_id",
        {
            "athlete_id": webhook_athlete_event_json["owner_id"],
        },
    )

    # Assertions
    assert response.status_code == 200
    assert not test_saved_strava_access_obj["scope"]


@pytest.mark.asyncio
async def test_validate_webhook_subscription(test_client: AsyncClient) -> None:

    endpoint = "/vendors/strava/webhook"
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": os.getenv("VERIFY_TOKEN"),
        "hub.challenge": "something from strava",
    }

    response = await test_client.get(endpoint, params=params)
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert WebhookVerificationResponse(**response_data)
    assert response_data["hub.challenge"] == "something from strava"


@pytest.mark.asyncio
async def test_receive_authorization_code(
    test_client: AsyncClient, test_db: Database, inserted_user_object: UserInDb
) -> None:

    endpoint = "/vendors/strava/authorize"
    params = {
        "user_id": inserted_user_object.id,
        "code": "something from strava",
        "scope": "activity:read_all,read_all",
    }

    response = await test_client.get(endpoint, params=params)

    test_saved_strava_access_obj = await test_db.fetch_one(
        "SELECT * FROM strava_access WHERE user_id=:user_id",
        {
            "user_id": inserted_user_object.id,
        },
    )

    # Assertions
    assert response.status_code == 200
    assert StravaAccessInDb(**test_saved_strava_access_obj)
    assert test_saved_strava_access_obj["scope"] == ["activity:read_all", "read_all"]
