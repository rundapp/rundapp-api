from typing import List, Optional

from app.usecases.interfaces.repos.challenges import IChallengesRepo
from app.usecases.interfaces.repos.users import IUsersRepo
from app.usecases.interfaces.services.challange_manager import IChallengeManager
from app.usecases.interfaces.services.email_manager import IEmailManager
from app.usecases.interfaces.services.signature_manager import ISignatureManager
from app.usecases.schemas.challenges import (
    BountyVerification,
    ChallengeBase,
    ChallengeJoinPayment,
    IssueChallengeBody,
    RetrieveChallengesAdapter,
)
from app.usecases.schemas.users import Participants, UserBase


class ChallengeManager(IChallengeManager):
    def __init__(
        self,
        users_repo: IUsersRepo,
        challenges_repo: IChallengesRepo,
        signature_manager: ISignatureManager,
        email_manager: IEmailManager,
    ):
        self.users_repo = users_repo
        self.challenges_repo = challenges_repo
        self.signature_manager = signature_manager
        self.email_manager = email_manager

    async def handle_challenge_issuance(self, payload: IssueChallengeBody) -> None:
        """Handles a newly issued challenge."""

        # 1. See if users already exist. If not, create them.
        participants = await self.handle_users(
            challenger_email=payload.challenger_email,
            challenger_address=payload.challenger_address,
            challengee_email=payload.challengee_email,
            challengee_address=payload.challengee_address,
        )

        # 2. Create challenge.
        issued_challenge = await self.__create_new_challenge(
            participants=participants,
            bounty=payload.bounty,
            distance=payload.distance,
            pace=payload.pace,
        )

        # 3. Notify participants via email.
        await self.email_manager.challenge_issuance_notification(
            participants=participants, challenge=issued_challenge
        )

    async def handle_users(
        self,
        challenger_email: str,
        challenger_address: str,
        challengee_email: str,
        challengee_address: Optional[str] = None,
    ) -> Participants:
        """Retrieves or creates users."""

        challenger = await self.users_repo.retrieve(email=challenger_email)
        if not challenger:
            challenger = await self.users_repo.create(
                new_user=UserBase(email=challenger_email, address=challenger_address)
            )

        challengee = await self.users_repo.retrieve(email=challengee_email)
        if not challengee:
            challengee = await self.users_repo.create(
                new_user=UserBase(email=challengee_email, address=challengee_address)
            )

        return Participants(challenger=challenger, challengee=challengee)

    async def __create_new_challenge(
        self,
        participants: Participants,
        bounty: int,
        distance: float,
        pace: Optional[int],
    ) -> ChallengeJoinPayment:
        """Creates challenge."""

        # TODO: will likely have to convert to metric.

        return await self.challenges_repo.create(
            new_challenge=ChallengeBase(
                challenger=participants.challenger.id,
                challengee=participants.challengee.id,
                bounty=bounty,
                distance=distance,
                pace=pace,
            )
        )

    async def claim_bounty(self, address: str) -> List[BountyVerification]:
        """Performs actions necessary for a user to rightly claim a bounty."""

        # 1. See if any challenges have been fulfilled pertaining to this user.
        completed_challenges = await self.challenges_repo.retrieve_many(
            query_params=RetrieveChallengesAdapter(
                challengee_address=address, challenge_complete=True
            )
        )

        # If there are multipe, needs to return a list of them
        bounty_verifications = []
        for challenge in completed_challenges:
            if not challenge.payment_complete:
                signed_message = await self.signature_manager.sign(
                    challenge_id=challenge.id
                )
                bounty_verifications.append(
                    BountyVerification(
                        **signed_message.dict(), challenge_id=challenge.id
                    )
                )

        return bounty_verifications
