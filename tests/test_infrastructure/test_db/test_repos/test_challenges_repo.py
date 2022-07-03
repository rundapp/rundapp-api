from typing import List

import pytest

from tests.conftest import DEFAULT_NUMBER_OF_INSERTED_OBJECTS
from app.usecases.interfaces.repos.challenges import IChallengesRepo
from app.usecases.schemas.challenges import ChallengeBase, ChallengeJoinPayment, RetrieveChallengesAdapter



@pytest.mark.asyncio
async def test_create(
    challenges_repo: IChallengesRepo,
    challenge_base: ChallengeBase
) -> None:

    test_challenge = await challenges_repo.create(new_challenge=challenge_base)

    assert isinstance(test_challenge, ChallengeJoinPayment)
    for key, value in challenge_base.dict().items():
        assert value == test_challenge.dict()[key]
    
    assert test_challenge.complete == False
    assert test_challenge.payment_complete == False


@pytest.mark.asyncio
async def test_retrieve(
    inserted_challenge_object: ChallengeJoinPayment,
    challenges_repo: IChallengesRepo,
) -> None:

    test_challenge = await challenges_repo.retrieve(id=inserted_challenge_object.id)

    assert isinstance(test_challenge, ChallengeJoinPayment)
    for key, value in test_challenge.dict().items():
        assert value == inserted_challenge_object.dict()[key]
    


@pytest.mark.asyncio
async def test_retrieve_many(
    many_inserted_challenge_objects: List[ChallengeJoinPayment],
    challenges_repo: IChallengesRepo,
) -> None:

    test_challenges = await challenges_repo.retrieve_many(query_params=RetrieveChallengesAdapter(challenge_complete=False))

    assert isinstance(test_challenges, List[ChallengeJoinPayment])
    assert len(test_challenges) == DEFAULT_NUMBER_OF_INSERTED_OBJECTS


@pytest.mark.asyncio
async def test_update_challenge(
    inserted_challenge_object: ChallengeJoinPayment,
    challenges_repo: IChallengesRepo,
) -> None:

    assert not inserted_challenge_object.complete

    updated_test_challenge = await challenges_repo.update_challenge(id=inserted_challenge_object.id)

    assert isinstance(updated_test_challenge, ChallengeJoinPayment)
    assert updated_test_challenge.complete



@pytest.mark.asyncio
async def test_update_payment(
    inserted_challenge_object: ChallengeJoinPayment,
    challenges_repo: IChallengesRepo,
) -> None:

    assert not inserted_challenge_object.payment_complete
    
    await challenges_repo.update_payment(id=inserted_challenge_object.id)

    updated_test_challenge = await challenges_repo.retrieve(id=inserted_challenge_object.id)

    assert updated_test_challenge.payment_complete