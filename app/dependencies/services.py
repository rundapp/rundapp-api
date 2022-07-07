from fastapi import Depends

from app.dependencies import get_challenges_repo, get_strava_client, get_strava_repo
from app.dependencies.repos import get_users_repo
from app.usecases.interfaces.clients.strava import IStravaClient
from app.usecases.interfaces.repos.challenges import IChallengesRepo
from app.usecases.interfaces.repos.strava import IStravaRepo
from app.usecases.interfaces.repos.users import IUsersRepo
from app.usecases.interfaces.services.challange_validation import IChallengeValidation
from app.usecases.interfaces.services.email_manager import IEmailManager
from app.usecases.interfaces.services.signature_manager import ISignatureManager
from app.usecases.services.challenge_manager import ChallengeManager
from app.usecases.services.challenge_validation import ChallengeValidation
from app.usecases.services.email_manager import EmailManager
from app.usecases.services.signature_manager import SignatureManager


async def get_signature_manager_service() -> ISignatureManager:
    """Instantiates and returns the Signature Manger Service."""

    return SignatureManager()


async def get_email_manager_service(strava_repo: IStravaRepo = Depends(get_strava_repo)) -> IEmailManager:
    """Instantiates and returns the Email Manger Service."""

    return EmailManager(strava_repo=strava_repo)


async def get_challenge_validation_service(
    strava_client: IStravaClient = Depends(get_strava_client),
    strava_repo: IStravaRepo = Depends(get_strava_repo),
    challenges_repo: IChallengesRepo = Depends(get_challenges_repo),
    email_manager: IEmailManager = Depends(get_email_manager_service),
) -> IChallengeValidation:
    """Instantiates and returns the Challenge Validation Service."""

    return ChallengeValidation(
        strava_client=strava_client,
        strava_repo=strava_repo,
        challenges_repo=challenges_repo,
        email_manager=email_manager,
    )


async def get_challenge_manager_service(
    users_repo: IUsersRepo = Depends(get_users_repo),
    challenges_repo: IChallengesRepo = Depends(get_challenges_repo),
    signature_manager: ISignatureManager = Depends(get_signature_manager_service),
    email_manager: IEmailManager = Depends(get_email_manager_service),
) -> IChallengeValidation:
    """Instantiates and returns the Challenge Manger Service."""

    return ChallengeManager(
        challenges_repo=challenges_repo,
        users_repo=users_repo,
        signature_manager=signature_manager,
        email_manager=email_manager,
    )
