from typing import Any, Mapping

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.usecases.schemas.challenges import ChallengeJoinPayment, ClaimBountyResponse
from tests.constants import CHALLENGEE_ADDRESS


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

    response = await test_client.post(endpoint, data=issue_challenge_request_json)

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

    response = await test_client.post(endpoint, data=email_too_long_request)
    assert response.status_code == 422

    # FAIL: Address not 42 characters long
    address_too_long_request = issue_challenge_request_json.copy()
    address_too_long_request[
        "challenger_address"
    ] = "0xcF107AdC80c7F7b5eE430B52744F96e2D76681a276681a2"

    response = await test_client.post(endpoint, data=address_too_long_request)
    assert response.status_code == 422

    # FAIL: Missing email
    email_missing_request = issue_challenge_request_json.copy()
    del email_missing_request["challengee_email"]

    response = await test_client.post(endpoint, data=email_missing_request)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_claim_challenge_bounty(
    test_client: AsyncClient, inserted_challenge_object: ChallengeJoinPayment
) -> None:

    endpoint = "/public/challenges/actions/claim"

    response = await test_client.get(endpoint, params={"address": CHALLENGEE_ADDRESS})
    response_data = response.json()

    # Assertions
    assert response.status_code == 200
    assert ClaimBountyResponse(**response_data)
    assert inserted_challenge_object.id == response_data[0]["challenge_id"]


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
