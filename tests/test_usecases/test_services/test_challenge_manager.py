import uuid

import pytest
import pytest_asyncio
from databases import Database

from app.usecases.interfaces.services.challange_manager import IChallengeManager
from app.usecases.schemas.challenges import (
    BountyVerification,
    ChallengeJoinPaymentAndUsers,
    ChallengeNotFound,
    ChallengeUnauthorizedAction,
    IssueChallengeBody,
)
from tests.constants import TEST_CHALLENGE_ID_NOT_FOUND


@pytest_asyncio.fixture
async def issue_challenge_body() -> IssueChallengeBody:
    test_json = {
        "challenger_name": "Bob",
        "challengee_name": "Alice",
        "challenger_email": "challenger@testservice.com",
        "challengee_email": "challengee@testservice.com",
        "challenge_id": str(uuid.uuid4()),
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
        address=inserted_challenge_object.challengee_address
    )

    for bounty in verified_bounties:
        assert isinstance(bounty, BountyVerification)
    assert verified_bounties[0].challenge.id == inserted_challenge_object.id


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
        address=inserted_challenge_object.challengee_address
    )

    for bounty in verified_bounties:
        assert isinstance(bounty, BountyVerification)
    assert verified_bounties[0].challenge.id == inserted_challenge_object.id


@pytest.mark.asyncio
async def test_handle_bounty_payment(
    challenge_manager_service: IChallengeManager,
    inserted_challenge_for_payment_test: ChallengeJoinPaymentAndUsers,
    test_db: Database,
) -> None:

    await challenge_manager_service.handle_bounty_payment(
        challenge_id=inserted_challenge_for_payment_test.id
    )

    payment = await test_db.fetch_one(
        "SELECT * FROM payments WHERE payments.challenge_id = :challenge_id",
        {"challenge_id": inserted_challenge_for_payment_test.id},
    )

    assert payment["complete"]


@pytest.mark.asyncio
async def test_handle_bounty_payment_unauthorized(
    challenge_manager_service: IChallengeManager,
    inserted_challenge_object: ChallengeJoinPaymentAndUsers,
    test_db: Database,
) -> None:

    with pytest.raises(ChallengeUnauthorizedAction):
        await challenge_manager_service.handle_bounty_payment(
            challenge_id=inserted_challenge_object.id
        )

    payment = await test_db.fetch_one(
        "SELECT * FROM payments WHERE payments.challenge_id = :challenge_id",
        {"challenge_id": inserted_challenge_object.id},
    )

    assert not payment["complete"]


@pytest.mark.asyncio
async def test_handle_bounty_payment_not_found(
    challenge_manager_service: IChallengeManager,
    inserted_challenge_object: ChallengeJoinPaymentAndUsers,
    test_db: Database,
) -> None:

    with pytest.raises(ChallengeNotFound):
        await challenge_manager_service.handle_bounty_payment(
            challenge_id=TEST_CHALLENGE_ID_NOT_FOUND
        )

    payment = await test_db.fetch_one(
        "SELECT * FROM payments WHERE payments.challenge_id = :challenge_id",
        {"challenge_id": inserted_challenge_object.id},
    )

    assert not payment["complete"]
