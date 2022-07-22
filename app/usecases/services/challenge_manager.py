from typing import List, Optional

import asyncio

from app.usecases.interfaces.clients.ethereum import IEthereumClient
from app.usecases.interfaces.repos.challenges import IChallengesRepo
from app.usecases.interfaces.repos.users import IUsersRepo
from app.usecases.interfaces.services.challange_manager import IChallengeManager
from app.usecases.interfaces.services.conversion_manager import IConversionManager
from app.usecases.interfaces.services.email_manager import IEmailManager
from app.usecases.interfaces.services.signature_manager import ISignatureManager
from app.usecases.schemas.challenges import (
    BountyVerification,
    ChallengeException,
    ChallengeJoinPaymentAndUsers,
    ChallengeNotFound,
    ChallengeOnChain,
    ChallengeUnauthorizedAction,
    CreateChallengeRepoAdapter,
    IssueChallengeBody,
    RetrieveChallengesAdapter,
)
from app.usecases.schemas.users import Participants, UserBase


class ChallengeManager(IChallengeManager):
    def __init__(
        self,
        ethereum_client: IEthereumClient,
        users_repo: IUsersRepo,
        challenges_repo: IChallengesRepo,
        signature_manager: ISignatureManager,
        email_manager: IEmailManager,
        conversion_manager: IConversionManager,
    ):
        self.ethereum_client = ethereum_client
        self.users_repo = users_repo
        self.challenges_repo = challenges_repo
        self.signature_manager = signature_manager
        self.email_manager = email_manager
        self.conversion_manager = conversion_manager

    async def handle_challenge_issuance(self, payload: IssueChallengeBody) -> None:
        """Handles a newly issued challenge."""

        # 1. Ensure challenge is not already in database.
        challenge = await self.challenges_repo.retrieve(id=payload.challenge_id)

        if challenge:
            raise ChallengeException("Invalid challenge_id.")

        # 2. Retrive on-chain challenge.
        onchain_challenge = await self.__retrieve_onchain_challenge(
            challenge_id=payload.challenge_id
        )

        # 3. See if users already exist. If not, create them.
        participants = await self.handle_users(
            payload=payload,
            challenger_address=onchain_challenge.challenger,
            challengee_address=onchain_challenge.challengee,
        )

        # 4. Create challenge.
        issued_challenge = await self.__create_new_challenge(
            challenge_id=payload.challenge_id,
            participants=participants,
            bounty=onchain_challenge.bounty,
            distance=onchain_challenge.distance,
            pace=onchain_challenge.speed,
        )

        # 5. Unit conversion.
        issued_challenge.distance = self.conversion_manager.cm_to_miles(
            distance=issued_challenge.distance
        )
        issued_challenge.pace = (
            self.conversion_manager.cm_per_second_to_minutes_per_mile(
                pace=issued_challenge.pace
            )
        )
        issued_challenge.bounty = issued_challenge.bounty / 1e18

        # 6. Notify participants via email.
        await self.email_manager.challenge_issuance_notification(
            participants=participants, challenge=issued_challenge
        )

    async def handle_users(
        self,
        payload: IssueChallengeBody,
        challenger_address: str,
        challengee_address: Optional[str] = None,
    ) -> Participants:
        """Retrieves or creates users."""

        challenger = await self.users_repo.retrieve(email=payload.challenger_email)
        if not challenger:
            challenger = await self.users_repo.create(
                new_user=UserBase(
                    email=payload.challenger_email,
                    address=challenger_address,
                    name=payload.challenger_name,
                )
            )

        challengee = await self.users_repo.retrieve(email=payload.challengee_email)
        if not challengee:
            challengee = await self.users_repo.create(
                new_user=UserBase(
                    email=payload.challengee_email,
                    address=challengee_address,
                    name=payload.challengee_name,
                )
            )

        return Participants(challenger=challenger, challengee=challengee)

    async def __create_new_challenge(
        self,
        challenge_id: str,
        participants: Participants,
        bounty: int,
        distance: float,
        pace: Optional[int],
    ) -> ChallengeJoinPaymentAndUsers:
        """Creates challenge."""

        return await self.challenges_repo.create(
            new_challenge=CreateChallengeRepoAdapter(
                id=challenge_id,
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

        # If there are multiple, needs to return a list of them
        bounty_verifications = []
        for challenge in completed_challenges:
            if not challenge.payment_complete:
                signed_message = await self.signature_manager.sign(
                    challenge_id=challenge.id
                )

                user = await self.users_repo.retrieve(id=challenge.challenger)
                challenge.challenger_address = user.address

                bounty_verifications.append(
                    BountyVerification(**signed_message.dict(), challenge=challenge)
                )

        return bounty_verifications

    async def handle_bounty_payment(self, challenge_id: str) -> None:
        """Checks and updates challenge payment completion."""

        onchain_challenge = await self.__retrieve_onchain_challenge(challenge_id=challenge_id)

        if not onchain_challenge.complete:
            raise ChallengeUnauthorizedAction("On-chain challenge not complete.")

        await self.challenges_repo.update_payment(id=challenge_id)

    async def __retrieve_onchain_challenge(self, challenge_id: str) -> ChallengeOnChain:
        """Retrieves challenge saved on-chain."""

        # 1. Sleep 3 seconds, before checking for on-chain challenge
        await asyncio.sleep(3)

        # 2. Get challenge
        onchain_challenge = self.ethereum_client.get_challenge(
            challenge_id=challenge_id
        )

        # 3. Ensure the challenge exists.
        if not int(onchain_challenge.challengee, 0) or not int(
            onchain_challenge.challenger, 0
        ):
            raise ChallengeNotFound("On-chain challenge not found.")

        return onchain_challenge
