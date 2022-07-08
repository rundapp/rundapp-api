from typing import Any, Mapping, Tuple

import pytest
import pytest_asyncio
from databases import Database
from httpx import AsyncClient

from app.usecases.interfaces.services.challange_validation import IChallengeValidation
from app.usecases.schemas.challenges import (
    ChallengeJoinPayment,
    ChallengeJoinPaymentAndUsers,
    ClaimBountyResponse,
)
from app.usecases.schemas.strava import StravaAccessInDb, WebhookEvent
from tests.constants import (
    CHALLENGE_FAILING_ACTIVITY_ID,
    CHALLENGE_PASSING_ACTIVITY_ID,
    CHALLENGEE_ADDRESS,
    TEST_ATHLETE_ID,
)


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


@pytest_asyncio.fixture
async def issue_challenge_request_json() -> Mapping[str, Any]:
    return {
        "challenger_email": "challenger@test.com",
        "challengee_email": "challengee@test.com",
        "challengee_address": "0xcF107AdC80c7F7b5eE430B52744F96e2D76681a2",
        "challenger_address": "0x63958fDFA9DAF21bb9bE4312c3f53cb080DA80D8",
        "bounty": 1000000000000,
        "distance": 10.0,
        "pace": 480,
    }


@pytest.mark.asyncio
async def test_issue_challenge(
    test_client: AsyncClient, issue_challenge_request_json: Mapping[str, Any]
) -> None:

    endpoint = "/public/challenges/actions/create"

    response = await test_client.post(endpoint, json=issue_challenge_request_json)

    # Assertions
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_issue_challenge_invalid_request(
    test_client: AsyncClient, issue_challenge_request_json: Mapping[str, Any]
) -> None:
    """Tests failure modes."""

    endpoint = "/public/challenges/actions/create"

    # FAIL: Email too long
    email_too_long_request = issue_challenge_request_json.copy()
    email_too_long_request[
        "challenger_email"
    ] = "0xcF107AdC80c7F7b5eE430B52744F96e2D76681a20xcF107AdC80c7F7b5eE430B52744F96e2D76681a2e2D76681a2@test.com"

    response = await test_client.post(endpoint, json=email_too_long_request)
    assert response.status_code == 422

    # FAIL: Address not 42 characters long
    address_too_long_request = issue_challenge_request_json.copy()
    address_too_long_request[
        "challenger_address"
    ] = "0xcF107AdC80c7F7b5eE430B52744F96e2D76681a276681a2"

    response = await test_client.post(endpoint, json=address_too_long_request)
    assert response.status_code == 422

    # FAIL: Missing email
    email_missing_request = issue_challenge_request_json.copy()
    del email_missing_request["challengee_email"]

    response = await test_client.post(endpoint, json=email_missing_request)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_claim_challenge_bounty(
    test_client: AsyncClient,
    inserted_challenge_object: ChallengeJoinPaymentAndUsers,
    test_db: Database,
) -> None:

    await test_db.execute(
        "UPDATE challenges SET complete = True WHERE id=:id",
        {
            "id": inserted_challenge_object.id,
        },
    )

    # 2. Hit endpoint
    endpoint = "/public/challenges/actions/claim"
    response = await test_client.get(endpoint, params={"address": CHALLENGEE_ADDRESS})
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert ClaimBountyResponse(**response_data)
    assert (
        inserted_challenge_object.id
        == response_data["verified_bounties"][0]["challenge_id"]
    )


@pytest.mark.asyncio
async def test_claim_challenge_bounty_invalid_address(
    test_client: AsyncClient, inserted_challenge_object: ChallengeJoinPayment
) -> None:
    """Fail: Address too long."""

    endpoint = "/public/challenges/actions/claim"

    response = await test_client.get(
        endpoint, params={"address": CHALLENGEE_ADDRESS + "F107"}
    )

    # Assertions
    assert response.status_code == 422
