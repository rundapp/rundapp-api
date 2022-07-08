from typing import List

import pytest
import pytest_asyncio
from databases import Database

from app.usecases.interfaces.services.challange_manager import IChallengeManager
from app.usecases.schemas.challenges import (
    BountyVerification,
    ChallengeJoinPaymentAndUsers,
    IssueChallengeBody,
)


@pytest_asyncio.fixture
async def issue_challenge_body() -> IssueChallengeBody:
    test_json = {
        "challenger_email": "challenger@testservice.com",
        "challengee_email": "challengee@testservice.com",
        "challengee_address": "0xcF107AdC80c7F7b5eE430B52744F96e2D76681a2",
        "challenger_address": "0x63958fDFA9DAF21bb9bE4312c3f53cb080DA80D8",
        "bounty": 1000000000000,
        "distance": 10.0,
        "pace": 480,
    }

    return IssueChallengeBody(**test_json)


@pytest.mark.asyncio
async def test_handle_challenge_issuance(
    challenge_manager_service: IChallengeManager,
    issue_challenge_body: IssueChallengeBody,
    test_db: Database,
) -> None:

    await challenge_manager_service.handle_challenge_issuance(
        payload=issue_challenge_body
    )

    test_challenge = await test_db.fetch_one(
        "SELECT * FROM challenges INNER JOIN users ON challenges.challenger = users.id WHERE users.email=:email",
        {
            "email": issue_challenge_body.challenger_email,
        },
    )

    assert test_challenge
    # TODO: test explicit values once converstion is decided upon


@pytest.mark.asyncio
async def test_claim_bounty(
    challenge_manager_service: IChallengeManager,
    inserted_challenge_object: ChallengeJoinPaymentAndUsers,
    test_db: Database,
) -> None:

    await test_db.execute(
        "UPDATE challenges SET complete = True WHERE id=:id",
        {
            "id": inserted_challenge_object.id,
        },
    )

    verified_bounties = await challenge_manager_service.claim_bounty(
        address=inserted_challenge_object.address
    )

    for bounty in verified_bounties:
        assert isinstance(bounty, BountyVerification)
    assert verified_bounties[0].challenge_id == inserted_challenge_object.id
