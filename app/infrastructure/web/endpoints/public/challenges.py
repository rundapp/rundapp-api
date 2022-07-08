from fastapi import APIRouter, Body, Depends, Query
from pydantic import constr

from app.dependencies import get_challenge_manager_service, get_users_repo
from app.libraries.errors import ApplicationErrors
from app.usecases.interfaces.repos.users import IUsersRepo
from app.usecases.interfaces.services.challange_manager import IChallengeManager
from app.usecases.schemas.challenges import (
    ChallengeException,
    ClaimBountyResponse,
    IssueChallengeBody,
)

challenges_router = APIRouter(tags=["Challenges"])


@challenges_router.post(
    "/actions/create",
    status_code=201,
    response_model=None,
)
async def issue_challenge(
    body: IssueChallengeBody = Body(...),
    challenge_manager_service: IChallengeManager = Depends(
        get_challenge_manager_service
    ),
) -> None:
    """Issues new challenge."""

    try:
        await challenge_manager_service.handle_challenge_issuance(payload=body)
    except ChallengeException as error:
        raise await ApplicationErrors(detail=str(error)).invalid_resource_id()


# @challenges_router.get(
#     "/",
#     status_code=200,
#     response_model=Something,
# )
# async def retreive_challenges(
#     challenges_repo: IChallengesRepo = Depends(get_challenges_repo),
# ) -> Something:
#     """Retreives many challenges."""


@challenges_router.get(
    "/actions/claim",
    status_code=200,
    response_model=ClaimBountyResponse,
)
async def claim_challenge_bounty(
    address: constr(min_length=42, max_length=42) = Query(...),
    users_repo: IUsersRepo = Depends(get_users_repo),
    challenge_manager_service: IChallengeManager = Depends(
        get_challenge_manager_service
    ),
) -> ClaimBountyResponse:
    """Allows users to claim a challenge's bounty."""

    user = await users_repo.retrieve(address=address)

    if not user:
        raise await ApplicationErrors(
            detail="The supplied address is invalid."
        ).invalid_resource_id()

    verified_bounties = await challenge_manager_service.claim_bounty(address=address)

    return ClaimBountyResponse(verified_bounties=verified_bounties)
